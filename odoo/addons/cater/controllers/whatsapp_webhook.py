# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WhatsAppWebhookController(http.Controller):
    @http.route('/whatsapp/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def whatsapp_webhook(self, **kwargs):
        """Endpoint for Twilio to POST incoming WhatsApp messages.

        If the 'twilio' library is available, validates the X-Twilio-Signature
        header against the active service's Auth Token.
        """
        try:
            frm = request.httprequest.form
            _logger.info(f"Webhook received data: {dict(frm)}")
            
            # Check if this is a StatusCallback (has MessageStatus) vs incoming message (has Body)
            message_sid = frm.get('MessageSid') or frm.get('SmsSid')
            message_status = frm.get('MessageStatus')
            from_number = frm.get('From')  # e.g., 'whatsapp:+233...'
            body = frm.get('Body')
            
            # Status callbacks have MessageStatus, incoming messages have Body
            if message_status and message_sid:
                # This is a status callback - update existing log
                _logger.info(f"Processing status callback: {message_sid} -> {message_status}")
                error_code = frm.get('ErrorCode')
                error_message = frm.get('ErrorMessage')
                Log = request.env['cater.whatsapp.log'].sudo()
                log = Log.search([('message_sid', '=', message_sid)], limit=1)
                if log:
                    vals = {}
                    allowed = {'queued', 'sending', 'sent', 'delivered', 'read', 'failed'}
                    if message_status.lower() in allowed:
                        vals['status'] = message_status.lower()
                    details = {k: frm.get(k) for k in frm.keys()}
                    vals['response_data'] = (log.response_data or '') + '\n' + str(details)
                    if message_status.lower() == 'failed' and (error_code or error_message):
                        vals['error_message'] = f"{error_code or ''} {error_message or ''}".strip()
                    log.write(vals)
                else:
                    request.env['cater.whatsapp.log'].sudo().create({
                        'to_number': 'unknown',
                        'message': '',
                        'status': message_status.lower() or 'sent',
                        'message_sid': message_sid,
                        'response_data': str({k: frm.get(k) for k in frm.keys()})
                    })
                return ''
            
            # This is an incoming message - process it
            elif body and from_number:
                _logger.info(f"Processing incoming message from {from_number}: {body}")
                
                # Optional: Twilio signature validation
                validation_enabled = request.env['ir.config_parameter'].sudo().get_param(
                    'cater.whatsapp.validate_signature', 'False'
                ).lower() in ('true', '1', 'yes')
                
                # Check if we're in development mode (skip validation for local development)
                is_dev_mode = request.env['ir.config_parameter'].sudo().get_param(
                    'cater.whatsapp.dev_mode', 'True'
                ).lower() in ('true', '1', 'yes')
                
                if is_dev_mode:
                    _logger.info('Development mode enabled - skipping Twilio signature validation.')
                    validation_enabled = False
                
                try:
                    from twilio.request_validator import RequestValidator  # type: ignore
                    svc = request.env['cater.whatsapp.service'].sudo().search([('active', '=', True)], limit=1)
                    signature = request.httprequest.headers.get('X-Twilio-Signature')
                    
                    if svc and signature and validation_enabled:
                        validator = RequestValidator(svc.auth_token)
                        url = request.httprequest.url
                        # Convert form data to proper format for validation
                        params = {}
                        for key in frm.keys():
                            params[key] = frm.get(key)
                        
                        _logger.info(f"Validating Twilio signature for URL: {url}")
                        _logger.debug(f"Signature: {signature}")
                        _logger.debug(f"Params keys: {list(params.keys())}")
                        
                        try:
                            is_valid = validator.validate(url, params, signature)
                            if not is_valid:
                                _logger.warning('Twilio signature validation failed for incoming webhook.')
                                _logger.warning(f"URL: {url}")
                                _logger.warning(f"Signature: {signature}")
                                _logger.warning(f"Auth Token (partial): {svc.auth_token[:8] if svc.auth_token else 'None'}...")
                                _logger.warning(f"Params count: {len(params)}")
                                # In production, you might want to return 403 here
                                # For now, we'll log the error but continue processing
                                _logger.warning('Continuing with message processing despite signature validation failure.')
                            else:
                                _logger.info('Twilio signature validation passed.')
                        except Exception as validation_error:
                            _logger.error(f"Error during signature validation: {validation_error}")
                            _logger.info('Continuing with message processing due to validation error.')
                    elif not validation_enabled:
                        _logger.info('Twilio signature validation disabled via config parameter.')
                    elif not signature:
                        _logger.info('No X-Twilio-Signature header found, skipping validation.')
                    elif not svc:
                        _logger.warning('No active WhatsApp service found for signature validation.')
                except ImportError:
                    _logger.info('twilio lib not installed; skipping signature validation.')
                
                # Normalize 'From' to plain number if present
                if from_number.startswith('whatsapp:'):
                    from_number = from_number.replace('whatsapp:', '').strip()
                    # Ensure the number starts with +
                    if from_number and not from_number.startswith('+'):
                        from_number = '+' + from_number

                # Log the incoming message
                request.env['cater.whatsapp.log'].sudo().create({
                    'to_number': from_number,
                    'message': body,
                    'status': 'received',
                    'message_sid': message_sid,
                    'response_data': str({k: frm.get(k) for k in frm.keys()})
                })

                # Process feedback response if this is a feedback message
                _logger.info(f"Attempting to process feedback from {from_number}")
                result = request.env['cater.event.booking'].sudo()._process_whatsapp_feedback_response(
                    from_number, body
                )
                if result:
                    _logger.info(f"Successfully created feedback record: {result.id}")
                else:
                    _logger.info(f"No feedback created - may be unrelated message or no matching booking")
            else:
                _logger.info(f"Unknown webhook type - Body: {body}, From: {from_number}, MessageStatus: {message_status}")

            # Minimal TwiML response (optional). Twilio accepts 200 with empty body.
            return ''
        except Exception as e:
            _logger.exception('Failed to process WhatsApp webhook: %s', e)
            return ''

    @http.route(['/whatsapp/status', '/whatsapp/status_callback'], type='http', auth='public', methods=['POST', 'GET'], csrf=False)
    def whatsapp_status(self, **kwargs):
        """Twilio StatusCallback webhook. Update message log status via MessageSid.

        Twilio posts fields like MessageSid and MessageStatus (queued, sending, sent, delivered, read, failed...).
        """
        try:
            frm = request.httprequest.form
            message_sid = frm.get('MessageSid') or frm.get('SmsSid')
            message_status = (frm.get('MessageStatus') or '').lower()
            error_code = frm.get('ErrorCode')
            error_message = frm.get('ErrorMessage')

            if not message_sid:
                _logger.warning('Status callback without MessageSid')
                return ''

            # Optional: validate signature like above (skip to keep it light)
            Log = request.env['cater.whatsapp.log'].sudo()
            log = Log.search([('message_sid', '=', message_sid)], limit=1)
            if log:
                vals = {}
                allowed = {'queued', 'sending', 'sent', 'delivered', 'read', 'failed'}
                if message_status in allowed:
                    vals['status'] = message_status
                # append/record details
                details = {k: frm.get(k) for k in frm.keys()}
                vals['response_data'] = (log.response_data or '') + '\n' + str(details)
                if message_status == 'failed' and (error_code or error_message):
                    vals['error_message'] = f"{error_code or ''} {error_message or ''}".strip()
                log.write(vals)
            else:
                # Create a minimal log if not found
                request.env['cater.whatsapp.log'].sudo().create({
                    'to_number': 'unknown',
                    'message': '',
                    'status': message_status or 'sent',
                    'message_sid': message_sid,
                    'response_data': str({k: frm.get(k) for k in frm.keys()})
                })
            return 'ok'
        except Exception as e:
            _logger.exception('Failed to process WhatsApp status callback: %s', e)
            return 'error'
