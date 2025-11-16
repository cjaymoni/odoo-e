from . import models
from . import controllers
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """ 
    Post-init hook to ensure ExpressPay provider is properly configured.
    This runs after the data file is loaded.
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Find the ExpressPay provider created by the data file
    expresspay_provider = env['payment.provider'].search([('code', '=', 'expresspay')])
    
    if expresspay_provider:
        # Ensure it's in test mode and has basic configuration
        expresspay_provider.write({
            'state': 'test',  # Ensure it starts in test mode
            'allow_tokenization': False,
            'allow_express_checkout': False,
        })
        _logger.info("ExpressPay provider configured successfully")
    else:
        # Fallback: Create the provider if data file didn't work
        env['payment.provider'].create({
            'name': 'ExpressPay Ghana',
            'code': 'expresspay',
            'state': 'test',
            'expresspay_merchant_id': 'TEST_MERCHANT_ID',
            'expresspay_api_key': 'TEST_API_KEY_1234567890',
        })
        _logger.warning("ExpressPay provider created via fallback hook")

def uninstall_hook(cr, registry):
    """ 
    Cleanup when module is uninstalled.
    Disable the provider but don't delete it to maintain referential integrity.
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    
    expresspay_provider = env['payment.provider'].search([('code', '=', 'expresspay')])
    if expresspay_provider:
        expresspay_provider.write({
            'state': 'disabled',
            # Optionally clear sensitive data
            'expresspay_merchant_id': False,
            'expresspay_api_key': False,
        })
        _logger.info("ExpressPay provider disabled during uninstall")