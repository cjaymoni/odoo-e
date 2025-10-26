import requests
import json
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class WhatsAppService(models.Model):
    _name = 'cater.whatsapp.service'
    _description = 'WhatsApp Integration Service'

    name = fields.Char('Service Name', default='WhatsApp Service')
    api_url = fields.Char('API URL', default='https://api.twilio.com/2010-04-01/Accounts/')
    account_sid = fields.Char('Account SID', required=True)
    auth_token = fields.Char('Auth Token', required=True)
    from_number = fields.Char('From Number', required=True, help='Your WhatsApp Business number')
    messaging_service_sid = fields.Char('Messaging Service SID', help='Optional. Use a Twilio Messaging Service (recommended). If set, "From" is ignored.')
    active = fields.Boolean('Active', default=True)

    def _twilio_messages_url(self):
        self.ensure_one()
        base = self.api_url.rstrip('/')
        return f"{base}/{self.account_sid}/Messages.json"

    def _twilio_account_url(self):
        self.ensure_one()
        base = self.api_url.rstrip('/')
        return f"{base}/{self.account_sid}.json"

    def _status_callback_url(self):
        """Build the public StatusCallback URL using web.base.url if set.

        Returns a string or None when not configured.
        """
        base_url = (self.env['ir.config_parameter'].sudo().get_param('web.base.url') or '').strip()
        if not base_url:
            _logger.debug("No web.base.url set; omitting StatusCallback")
            return None
        lowered = base_url.lower()
        if not (lowered.startswith('http://') or lowered.startswith('https://')):
            _logger.debug("web.base.url is not http(s): %s; omitting StatusCallback", base_url)
            return None
        # Avoid localhost/127.* which Twilio rejects
        if 'localhost' in lowered or '127.0.0.1' in lowered:
            _logger.info("web.base.url points to localhost; skipping StatusCallback to avoid Twilio 400")
            return None
        return base_url.rstrip('/') + '/whatsapp/webhook'

    def action_test_connection(self):
        """UI action to test Twilio credentials/connectivity."""
        self.ensure_one()
        ok, msg = self.test_connection()
        message = msg if msg else ("Twilio connection ok" if ok else "Twilio connection failed")
        msg_type = 'success' if ok else 'danger'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Twilio Test'),
                'message': message,
                'sticky': False,
                'type': msg_type,
            }
        }

    def test_connection(self):
        """Return (ok: bool, message: str). Performs a simple GET to the Account endpoint."""
        self.ensure_one()
        url = self._twilio_account_url()
        try:
            resp = requests.get(url, auth=(self.account_sid, self.auth_token), timeout=15)
            if resp.status_code == 200:
                return True, _('Twilio credentials verified.')
            try:
                data = resp.json()
                err = data.get('message') or resp.text
            except ValueError:
                err = resp.text
            return False, _('HTTP %s: %s') % (resp.status_code, err)
        except requests.RequestException as rexc:
            return False, _('Network error: %s') % rexc
        except Exception as exc:
            return False, _('Unexpected error: %s') % exc
    
    def send_message(self, to_number, message):
        """Send a WhatsApp message via Twilio.

        Returns True if Twilio accepted (201) otherwise False.
        Creates a log record for every attempt.
        """
        self.ensure_one()

        if not self.active:
            _logger.info("WhatsApp service inactive - skipping send.")
            return False

        if not to_number:
            _logger.warning("No destination number provided for WhatsApp message.")
            return False

        # Basic formatting safeguard (expect E.164 with +)
        if not to_number.startswith('+'):
            _logger.warning("Destination number %s not in E.164 format (missing '+').", to_number)

        url = self._twilio_messages_url()
        payload = {
            'To': f'whatsapp:{to_number}',
            'Body': message
        }
        # Prefer Messaging Service when provided
        if self.messaging_service_sid:
            payload['MessagingServiceSid'] = self.messaging_service_sid
        else:
            payload['From'] = f'whatsapp:{self.from_number}'

        # Add StatusCallback if a base URL is configured so we can track delivery
        cb_url = self._status_callback_url()
        if cb_url:
            payload['StatusCallback'] = cb_url

        try:
            response = requests.post(
                url,
                data=payload,
                auth=(self.account_sid, self.auth_token),
                timeout=15
            )
        except requests.RequestException as rexc:
            err = f"Network/requests error: {rexc}"
            _logger.error(err)
            self.env['cater.whatsapp.log'].create({
                'to_number': to_number,
                'message': message,
                'status': 'error',
                'error_message': err
            })
            return False
        except Exception as e:  # Catch-all
            err = f"Unexpected error: {e}"
            _logger.exception(err)
            self.env['cater.whatsapp.log'].create({
                'to_number': to_number,
                'message': message,
                'status': 'error',
                'error_message': err
            })
            return False

        success = response.status_code in (200, 201)
        log_vals = {
            'to_number': to_number,
            'message': message,
        }

        # Parse JSON for richer logging if possible
        try:
            resp_json = response.json()
            if success:
                # Capture Twilio SID and initial status (queued/sending/sent)
                log_vals['message_sid'] = resp_json.get('sid')
                tw_status = (resp_json.get('status') or '').lower()
                allowed = {'queued', 'sending', 'sent', 'delivered', 'read'}
                log_vals['status'] = tw_status if tw_status in allowed else 'sent'
                log_vals['response_data'] = json.dumps({
                    'sid': resp_json.get('sid'),
                    'status': resp_json.get('status'),
                    'num_segments': resp_json.get('num_segments'),
                })
            else:
                error_msg = resp_json.get('message') or response.text
                log_vals['status'] = 'failed'
                log_vals['error_message'] = f"{response.status_code}: {error_msg}"
        except ValueError:  # Not JSON
            if success:
                log_vals['status'] = 'sent'
                log_vals['response_data'] = response.text
            else:
                log_vals['status'] = 'failed'
                log_vals['error_message'] = f"{response.status_code}: {response.text}"

        self.env['cater.whatsapp.log'].create(log_vals)
        if not success:
            _logger.warning("WhatsApp send failed (%s): %s", response.status_code, log_vals.get('error_message'))
        else:
            _logger.info("WhatsApp message accepted by Twilio: %s", log_vals.get('response_data'))
        return success

    def send_template(self, to_number, content_sid, variables=None):
        """Send a WhatsApp message using a Twilio Content Template.

        - content_sid: Twilio Content SID (e.g., HXxxxxxxxx...)
        - variables: dict of variable mappings for the template, serialized to ContentVariables
        Returns True if accepted (201/200), else False.
        """
        self.ensure_one()

        if not self.active:
            _logger.info("WhatsApp service inactive - skipping send.")
            return False

        if not to_number:
            _logger.warning("No destination number provided for WhatsApp template message.")
            return False

        if not content_sid:
            _logger.warning("No Content SID provided for WhatsApp template message.")
            return False

        if not to_number.startswith('+'):
            _logger.warning("Destination number %s not in E.164 format (missing '+').", to_number)

        url = self._twilio_messages_url()
        payload = {
            'To': f'whatsapp:{to_number}',
            'ContentSid': content_sid,
        }
        if variables:
            try:
                payload['ContentVariables'] = json.dumps(variables)
            except Exception:
                # Fallback to string cast if variables isn't JSON-serializable
                payload['ContentVariables'] = str(variables)

        if self.messaging_service_sid:
            payload['MessagingServiceSid'] = self.messaging_service_sid
        else:
            payload['From'] = f'whatsapp:{self.from_number}'

        cb_url = self._status_callback_url()
        if cb_url:
            payload['StatusCallback'] = cb_url

        try:
            response = requests.post(
                url,
                data=payload,
                auth=(self.account_sid, self.auth_token),
                timeout=15
            )
        except requests.RequestException as rexc:
            err = f"Network/requests error: {rexc}"
            _logger.error(err)
            self.env['cater.whatsapp.log'].create({
                'to_number': to_number,
                'message': f"Template:{content_sid} vars:{variables}",
                'status': 'error',
                'error_message': err
            })
            return False
        except Exception as e:
            err = f"Unexpected error: {e}"
            _logger.exception(err)
            self.env['cater.whatsapp.log'].create({
                'to_number': to_number,
                'message': f"Template:{content_sid} vars:{variables}",
                'status': 'error',
                'error_message': err
            })
            return False

        success = response.status_code in (200, 201)
        log_vals = {
            'to_number': to_number,
            'message': f"Template:{content_sid} vars:{variables}",
        }
        try:
            resp_json = response.json()
            if success:
                log_vals['message_sid'] = resp_json.get('sid')
                tw_status = (resp_json.get('status') or '').lower()
                allowed = {'queued', 'sending', 'sent', 'delivered', 'read'}
                log_vals['status'] = tw_status if tw_status in allowed else 'sent'
                log_vals['response_data'] = json.dumps({
                    'sid': resp_json.get('sid'),
                    'status': resp_json.get('status'),
                    'num_segments': resp_json.get('num_segments'),
                })
            else:
                error_msg = resp_json.get('message') or response.text
                log_vals['status'] = 'failed'
                log_vals['error_message'] = f"{response.status_code}: {error_msg}"
        except ValueError:
            if success:
                log_vals['status'] = 'sent'
                log_vals['response_data'] = response.text
            else:
                log_vals['status'] = 'failed'
                log_vals['error_message'] = f"{response.status_code}: {response.text}"

        self.env['cater.whatsapp.log'].create(log_vals)
        if not success:
            _logger.warning("WhatsApp template send failed (%s): %s", response.status_code, log_vals.get('error_message'))
        else:
            _logger.info("WhatsApp template accepted by Twilio: %s", log_vals.get('response_data'))
        return success

class WhatsAppLog(models.Model):
    _name = 'cater.whatsapp.log'
    _description = 'WhatsApp Message Log'
    _order = 'create_date desc'

    def init(self):
        """Create database indexes for performance"""
        super().init()
        # Create indexes using SQL
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_whatsapp_log_message_sid 
            ON cater_whatsapp_log(message_sid) 
            WHERE message_sid IS NOT NULL;
        """)

    to_number = fields.Char('To Number', required=True)
    message = fields.Text('Message', required=True)
    status = fields.Selection([
        ('queued', 'Queued'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('received', 'Received'),
        ('failed', 'Failed'),
        ('error', 'Error')
    ], 'Status', required=True)
    message_sid = fields.Char('Twilio SID')
    response_data = fields.Text('Response Data')
    error_message = fields.Text('Error Message')
    send_date = fields.Datetime('Send Date', default=fields.Datetime.now)
