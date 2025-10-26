import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug import urls

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('expresspay', 'ExpressPay Ghana')],
        ondelete={'expresspay': 'set default'}
    )

    expresspay_merchant_id = fields.Char(
        string="Merchant ID",
        required_if_provider='expresspay',
        groups='base.group_system'
    )
    expresspay_api_key = fields.Char(
        string="API Key",
        required_if_provider='expresspay',
        groups='base.group_system'
    )

    expresspay_base_url = fields.Char(
        string="Base URL for Webhooks",
        required_if_provider='expresspay',
        default='https://localhost:8069',
        help="Base URL for webhook and callback URLs (e.g., https://yourdomain.com or https://localhost:8069 for local development)",
        groups='base.group_system'
    )

    expresspay_enable_webhooks = fields.Boolean(
        string="Enable Webhooks",
        default=True,
        help="If enabled, ExpressPay will send transaction status updates via webhooks to your configured base URL.",
        groups='base.group_system'
    )

    expresspay_fallback_polling = fields.Boolean(
        string="Enable Fallback Polling",
        default=False,
        help="If enabled, the system will periodically poll ExpressPay for transaction status updates if webhooks are not available or fail to deliver.",
        groups='base.group_system'
    )

    def _get_default_payment_method_codes(self):
        res = super()._get_default_payment_method_codes()
        res.append('expresspay')
        return res

    def _compute_feature_support(self):
        super()._compute_feature_support()
        self.filtered(lambda p: p.code == 'expresspay').update({
            'fees': False,
            'tokenization': False,
            'refund': 'partial',
        })

    def _expresspay_make_request(self, endpoint, payload=None, method='POST'):
        """Make API request to ExpressPay (from your implementation)"""
        self.ensure_one()
        base_url = "https://sandbox.expresspaygh.com/api/" if self.state == 'test' else "https://expresspaygh.com/api/"
        url = f"{base_url}{endpoint}"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        data = payload or {}
        data['merchant-id'] = self.expresspay_merchant_id
        data['api-key'] = self.expresspay_api_key
        
        try:
            if method == 'POST':
                response = requests.post(url, data=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, params=data, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error("ExpressPay API request failed: %s", str(e))
            raise ValidationError(_("ExpressPay API connection failed: %s") % str(e))
        except ValueError as e:
            _logger.error("ExpressPay API response parsing failed: %s", str(e))
            raise ValidationError(_("ExpressPay API response invalid"))

    def _expresspay_get_checkout_url(self):
        """Get the correct checkout URL based on environment"""
        self.ensure_one()
        if self.state == 'test':
            return "https://sandbox.expresspaygh.com/api/checkout.php"
        return "https://expresspaygh.com/api/checkout.php"

    def _expresspay_get_base_url(self):
        """Get the configured base URL for webhooks and callbacks"""
        self.ensure_one()
        if not self.expresspay_base_url:
            # Fallback to localhost if not configured
            return "https://localhost:8069"
        return self.expresspay_base_url.rstrip('/')

    def _expresspay_should_use_webhooks(self):
        """Determine if webhooks should be used based on configuration"""
        self.ensure_one()
        return self.expresspay_enable_webhooks and self.expresspay_base_url

    def _expresspay_should_use_fallback_polling(self):
        """Determine if fallback polling should be used"""
        self.ensure_one()
        return self.expresspay_fallback_polling and not self.expresspay_enable_webhooks

    def _expresspay_query_status(self, *, token=None, order_id=None):
        """Query ExpressPay for the current status of a transaction."""
        self.ensure_one()
        if not token and not order_id:
            raise ValidationError(_("ExpressPay query requires token or order-id"))

        payload = {}
        if token:
            payload['token'] = token
        if order_id:
            payload['order-id'] = order_id

        # Query endpoint (GET is fine; the helper supports it)
        return self._expresspay_make_request('query.php', payload=payload, method='GET')

    @api.constrains('expresspay_base_url')
    def _check_expresspay_base_url(self):
        """Validate the base URL format"""
        for provider in self.filtered(lambda p: p.code == 'expresspay' and p.expresspay_base_url):
            base_url = provider.expresspay_base_url.strip()
            if not base_url:
                continue
                
            # Basic URL validation
            if not (base_url.startswith('http://') or base_url.startswith('https://')):
                raise ValidationError(_("Base URL must start with http:// or https://"))
            
            # Remove trailing slash if present
            if base_url.endswith('/'):
                provider.expresspay_base_url = base_url.rstrip('/')

    @api.constrains('is_published', 'expresspay_base_url')
    def _check_expresspay_base_url_when_published(self):
        """Ensure base URL is configured when provider is published"""
        for provider in self.filtered(lambda p: p.code == 'expresspay' and p.is_published):
            if not provider.expresspay_base_url or not provider.expresspay_base_url.strip():
                raise ValidationError(_("Base URL for webhooks must be configured when the ExpressPay provider is published"))
