from odoo import models, api, _
from odoo.exceptions import ValidationError
import logging
from werkzeug import urls


_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Two-step process: get token first, then prepare redirect (from your implementation)"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'expresspay':
            return res
        
        # Step 1: Submit payment details to get token
        base_url = self.provider_id._expresspay_get_base_url()
        safe_ref = self.reference.replace('/', '-')
        
        _logger.info("ExpressPay using base URL: %s for transaction %s", base_url, self.reference)
        
        payload = {
            'firstname': self.partner_id.name.split(' ')[0],
            'lastname': ' '.join(self.partner_id.name.split(' ')[1:]) or '-',
            'email': self.partner_email,
            'phonenumber': self.partner_phone or '0000000000',
            'currency': self.currency_id.name,
            'amount': str(self.amount),
            'order-id': safe_ref,
            'redirect-url': urls.url_join(base_url, '/payment/expresspay/return'),
        }
        
        # Add webhook URL if enabled
        if self.provider_id._expresspay_should_use_webhooks():
            payload['post-url'] = urls.url_join(base_url, '/payment/expresspay/webhook')
            _logger.info("ExpressPay webhooks enabled - using post-url: %s", payload['post-url'])
        else:
            _logger.info("ExpressPay webhooks disabled - relying on return URL only")
        
        _logger.info("ExpressPay Step 1 - Submitting payment details: %s", payload)
        
        try:
            response = self.provider_id._expresspay_make_request('submit.php', payload)
            _logger.info("ExpressPay Step 1 - API response: %s", response)
            
            # Check if Step 1 was successful
            status = response.get('status')
            if status != 1:
                _logger.error("ExpressPay Step 1 failed with status: %s, response: %s", status, response)
                raise ValidationError(_("ExpressPay payment initialization failed. Please try again."))
            
            # Step 2: Extract token from Step 1 response
            token = response.get('token')
            _logger.info("ExpressPay Step 2 - Extracted token: '%s' (type: %s)", token, type(token))
            
            if not token or str(token).strip() == '':
                _logger.error("ExpressPay Step 1 successful but no valid token returned: %s", response)
                raise ValidationError(_("ExpressPay payment initialization failed - no token received."))
            
            # Prepare checkout redirect URL with token (ensure token is string and not empty)
            token_str = str(token).strip()
            checkout_url = self.provider_id._expresspay_get_checkout_url()
            checkout_url_with_token = f"{checkout_url}?token={token_str}"
            _logger.info("ExpressPay Step 2 - Final checkout URL: %s", checkout_url_with_token)
            
            return {
                'checkout_url': self.provider_id._expresspay_get_checkout_url(),
                'token': token_str,
            }
            
        except Exception as e:
            _logger.error("ExpressPay API call failed: %s", str(e))
            raise ValidationError(_("ExpressPay payment processing failed: %s") % str(e))


    # def _get_specific_processing_values(self, processing_values):
    #     res = super()._get_specific_processing_values(processing_values)
    #     if self.provider_code == 'expresspay':
    #         # Get the rendering values which contain the redirect_url
    #         rendering_values = self._get_specific_rendering_values(processing_values)
    #         # Render the redirect form for ExpressPay
    #         res['redirect_form_html'] = self.env['ir.qweb']._render(
    #             'expresspay_ghana.expresspay_redirect_form',
    #             {
    #                 'redirect_url': rendering_values.get('redirect_url'),
    #             },
    #         )
    #     return res

    def _get_specific_processing_values(self, processing_values):
        """Build the provider-specific processing values for ExpressPay.

    Renders a GET form that posts the token as a hidden input instead of
    baking the token into the <form action="..."> URL. If only a single
    redirect_url is available (legacy), we split it to recover the base
    checkout URL and the token.
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'expresspay':
            return res

    # Ask rendering step for values (may be {'checkout_url','token'} or just {'redirect_url'})
        rendering_values = self._get_specific_rendering_values(processing_values) or {}

        checkout_url = rendering_values.get('checkout_url')
        token = rendering_values.get('token')

    # Backward-compat: if we only have redirect_url, split into base + token
        if (not checkout_url or not token) and rendering_values.get('redirect_url'):
            from urllib.parse import urlparse, parse_qs, urlunparse
            ru = rendering_values['redirect_url']
            parsed = urlparse(ru)
            q = parse_qs(parsed.query)

            token = token or (q.get('token', [None])[0])
        # Rebuild base URL without any query/fragment
            checkout_url = checkout_url or urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, '', '', '')
            )

    # Final safety: if checkout_url still missing, derive from provider; and sanitize token
        if not checkout_url:
            checkout_url = self.provider_id._expresspay_get_checkout_url()

        import re
        if token is None or str(token).strip() == '':
            raise ValidationError(_("ExpressPay: No token available to render the redirect form."))
        token = re.sub(r'[^\w\.-]', '', str(token)).strip()

    # Render the redirect form expected by views/payment_expresspay_templates.xml
        res['redirect_form_html'] = self.env['ir.qweb']._render(
            'expresspay_ghana.expresspay_redirect_form',
            {
            'checkout_url': checkout_url,  # <form action="...">
            'token': token,                # <input type="hidden" name="token" ...>
            },
        )
        return res



    def _expresspay_validate_transaction(self, feedback_data):
        """Validate transaction based on webhook data"""
        self.ensure_one()
        
        _logger.info("ExpressPay validating transaction %s with data: %s", self.reference, feedback_data)
        
        # ExpressPay API returns 'result' field, not 'response-code'
        response_code = feedback_data.get('result', feedback_data.get('response-code', '3'))
        state_mapping = {
            1: 'done',        # Approved/Completed (integer)
            '1': 'done',      # Approved/Completed (string)
            2: 'cancel',      # Cancelled by user (integer)
            '2': 'cancel',    # Cancelled by user (string)
            3: 'error',       # Declined/Failed (integer)
            '3': 'error',     # Declined/Failed (string)
            4: 'pending',     # Pending (integer)
            '4': 'pending',   # Pending (string)
            0: 'pending',     # Pending (integer)
            '0': 'pending',   # Pending (string)
        }

        target_state = state_mapping.get(response_code, 'error')
        _logger.info("ExpressPay transaction %s: response_code=%s, target_state=%s", 
                    self.reference, response_code, target_state)

        # Store ExpressPay reference
        expresspay_reference = feedback_data.get('token')
        if expresspay_reference:
            self._expresspay_set_reference_token(expresspay_reference)

        # Update transaction state
        if target_state == 'done':
            self._set_done()
            _logger.info("ExpressPay transaction %s completed successfully", self.reference)
        elif target_state == 'cancel':
            self._set_canceled()
            _logger.info("ExpressPay transaction %s was cancelled", self.reference)
        elif target_state == 'pending':
            self._set_pending()
            _logger.info("ExpressPay transaction %s is pending", self.reference)
        else:
            error_message = feedback_data.get('reason', _('Payment failed. Please try again.'))
            self._set_error(error_message)
            _logger.error("ExpressPay transaction %s failed: %s", self.reference, error_message)

        return True

    def _expresspay_get_reference_token(self):
        """Get the ExpressPay reference token from the appropriate field"""
        self.ensure_one()
        # Try provider_reference first (newer Odoo versions), then acquirer_reference
        return getattr(self, 'provider_reference', None) or getattr(self, 'acquirer_reference', None)

    def _expresspay_set_reference_token(self, token):
        """Set the ExpressPay reference token to the appropriate field"""
        self.ensure_one()
        if hasattr(self, 'provider_reference'):
            self.provider_reference = token
        elif hasattr(self, 'acquirer_reference'):
            self.acquirer_reference = token
        else:
            _logger.warning("No reference field found for transaction %s", self.reference)

    def _expresspay_poll_pending_payment(self):
        """Poll ExpressPay for pending payment status updates"""
        self.ensure_one()
        if not self.provider_id._expresspay_should_use_fallback_polling():
            return False
            
        try:
            # Query ExpressPay for current status
            token = self._expresspay_get_reference_token()
            if not token:
                _logger.error("No reference token found for transaction %s", self.reference)
                return False
                
            status_response = self.provider_id._expresspay_query_status(
                token=token,
                order_id=self.reference
            )
            
            _logger.info("ExpressPay fallback polling response: %s", status_response)
            
            # Process the status update
            self._expresspay_validate_transaction(status_response)
            return True
            
        except Exception as e:
            _logger.error("ExpressPay fallback polling failed: %s", str(e))
            return False

    def _expresspay_schedule_polling(self):
        """Schedule periodic polling for pending payments"""
        self.ensure_one()
        if not self.provider_id._expresspay_should_use_fallback_polling():
            return
            
        # Schedule polling every 2 minutes for pending payments
        if self.state == 'pending':
            self.env['ir.cron'].sudo().create({
                'name': f'ExpressPay Polling - TX {self.reference}',
                'model_id': self.env['ir.model']._get('payment.transaction').id,
                'state': 'code',
                'code': f'model._expresspay_poll_pending_payment()',
                'interval_number': 2,
                'interval_type': 'minutes',
                'numbercall': 15,  # Poll for 30 minutes max
                'active': True,
            })
            _logger.info("ExpressPay fallback polling scheduled for transaction %s", self.reference)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Find transaction from notification data (from your implementation)"""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'expresspay' or len(tx) == 1:
            return tx
            
        reference = notification_data.get('order-id')
        if not reference:
            raise ValidationError("ExpressPay: " + _("Received data with missing order-id."))
            
        # Search by reference (order-id)
        tx = self.search([
            ('reference', '=', reference), 
            ('provider_code', '=', 'expresspay')
        ])
        
        if not tx:
            raise ValidationError("ExpressPay: " + _("No transaction found matching order-id %s.", reference))
            
        return tx