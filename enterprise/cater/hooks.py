# -*- coding: utf-8 -*-
"""
Post-installation hooks for the catering module
"""
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Create GHS conversion rates for companies where base currency is not GHS
    This runs after module installation/upgrade
    """
    
    # Get GHS currency
    ghs_currency = env['res.currency'].search([('name', '=', 'GHS')], limit=1)
    if not ghs_currency:
        _logger.info("GHS currency not found, skipping GHS rate creation")
    else:
        # Ensure GHS and other standard currencies are active
        common_currencies = env['res.currency'].search([
            ('name', 'in', ['GHS', 'USD', 'GBP', 'EUR'])
        ])
        common_currencies.write({'active': True})
        _logger.info("Activated common currencies (GHS, USD, GBP, EUR)")
    
    # Define rates based on common base currencies
    rates_map = {
        'USD': 12.195,  # 1 USD = 12.195 GHS (inverse of 0.082)
        'GBP': 15.873,  # 1 GBP = 15.873 GHS (inverse of 0.063)
        'EUR': 13.333,  # 1 EUR = 13.333 GHS (inverse of 0.075)
    }
    
    # Process each company
    for company in env['res.company'].search([]):
        company_currency = company.currency_id
        
        # Skip if company currency is already GHS
        if company_currency.name == 'GHS':
            continue
        
        # Only create rate if company currency is in our map
        if company_currency.name in rates_map:
            rate_value = rates_map[company_currency.name]
            rate_date = (datetime.now() - timedelta(days=365)).date()
            
            # Check if rate already exists
            existing_rate = env['cater.currency.rate'].search([
                ('company_id', '=', company.id),
                ('currency_id', '=', ghs_currency.id),
                ('date', '=', rate_date)
            ], limit=1)
            
            if not existing_rate:
                try:
                    env['cater.currency.rate'].create({
                        'company_id': company.id,
                        'currency_id': ghs_currency.id,
                        'date': rate_date,
                        'rate': rate_value,
                        'active': True,
                    })
                    _logger.info(f"Created {company_currency.name} → GHS rate ({rate_value}) for company {company.name}")
                except Exception as e:
                    _logger.warning(f"Failed to create GHS rate for company {company.name}: {e}")
            else:
                _logger.info(f"GHS rate already exists for company {company.name} on {rate_date}")
