# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CaterCurrencyRate(models.Model):
    _name = 'cater.currency.rate'
    _description = 'Manual Currency Exchange Rates'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    company_id = fields.Many2one('res.company', 'Company', required=True, 
                                  default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                   domain="[('id', '!=', company_currency_id)]")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', 
                                          string='Base Currency', readonly=True)
    rate = fields.Float('Rate', required=True, digits=(12, 6),
                        help="1 unit of base currency = this many units of target currency")
    inverse_rate = fields.Float('Inverse Rate', compute='_compute_inverse_rate', 
                                 digits=(12, 6), readonly=True,
                                 help="1 unit of target currency = this many units of base currency")
    date = fields.Date('Date', required=True, default=fields.Date.context_today,
                       help="Date from which this rate is effective")
    active = fields.Boolean('Active', default=True)
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    _sql_constraints = [
        ('unique_currency_date_company', 
         'unique(currency_id, date, company_id)', 
         'Only one rate per currency per date per company is allowed!')
    ]
    
    
    @api.depends('currency_id', 'rate', 'date', 'company_currency_id')
    def _compute_display_name(self):
        """Compute display name for better readability"""
        for record in self:
            if record.currency_id and record.company_currency_id:
                record.display_name = f"1 {record.company_currency_id.name} = {record.rate:.4f} {record.currency_id.name} ({record.date})"
            else:
                record.display_name = 'New Exchange Rate'
    
    @api.depends('rate')
    def _compute_inverse_rate(self):
        """Calculate inverse rate for display"""
        for record in self:
            if record.rate and record.rate > 0:
                record.inverse_rate = 1.0 / record.rate
            else:
                record.inverse_rate = 0.0
    
    @api.constrains('rate')
    def _check_rate(self):
        """Validate that rate is positive"""
        for record in self:
            if record.rate <= 0:
                raise ValidationError(_('Exchange rate must be greater than zero!'))
    
    @api.model
    def get_conversion_rate(self, from_currency, to_currency, date=None):
        """
        Get conversion rate from one currency to another
        Returns the rate to multiply with the from_currency amount
        """
        if not date:
            date = fields.Date.context_today(self)
        
        _logger.info(f"get_conversion_rate: {from_currency.name} → {to_currency.name} on {date}")
        
        # If same currency, no conversion needed
        if from_currency == to_currency:
            _logger.info(f"Same currency, returning 1.0")
            return 1.0
        
        company_currency = self.env.company.currency_id
        _logger.info(f"Company currency: {company_currency.name}")
        
        # Case 1: From company currency to another currency
        if from_currency == company_currency:
            rate_record = self.search([
                ('currency_id', '=', to_currency.id),
                ('date', '<=', date),
                ('active', '=', True),
                ('company_id', '=', self.env.company.id)
            ], order='date desc', limit=1)
            
            if rate_record:
                _logger.info(f"Using user-defined rate: {rate_record.display_name}, rate={rate_record.rate}")
                return rate_record.rate
            else:
                _logger.warning(f"No user-defined exchange rate found in cater.currency.rate for {to_currency.name} on {date}. Please create a rate record.")
                return 0.0
        
        # Case 2: From another currency to company currency
        elif to_currency == company_currency:
            rate_record = self.search([
                ('currency_id', '=', from_currency.id),
                ('date', '<=', date),
                ('active', '=', True),
                ('company_id', '=', self.env.company.id)
            ], order='date desc', limit=1)
            
            if rate_record:
                _logger.info(f"Using user-defined rate: {rate_record.display_name}, inverse_rate={rate_record.inverse_rate}")
                return rate_record.inverse_rate
            else:
                _logger.warning(f"No user-defined exchange rate found in cater.currency.rate for {from_currency.name} on {date}. Please create a rate record.")
                return 0.0
        
        # Case 3: Between two foreign currencies (convert through company currency using defined rates)
        else:
            _logger.info(f"Converting between foreign currencies {from_currency.name} → {company_currency.name} → {to_currency.name}")
            # From -> Company Currency (using user-defined rate)
            from_to_company = self.get_conversion_rate(from_currency, company_currency, date)
            # Company Currency -> To (using user-defined rate)
            company_to_to = self.get_conversion_rate(company_currency, to_currency, date)
            
            if from_to_company and company_to_to:
                final_rate = from_to_company * company_to_to
                _logger.info(f"Calculated cross-currency rate: {from_to_company} × {company_to_to} = {final_rate}")
                return final_rate
            else:
                _logger.warning(f"Cannot convert {from_currency.name} → {to_currency.name}: missing required rates")
                return 0.0
    
    @api.model
    def convert_amount(self, amount, from_currency, to_currency, date=None):
        """
        Convert an amount from one currency to another
        """
        _logger.info(f"convert_amount called: {amount} from {from_currency.name} to {to_currency.name} on {date}")
        rate = self.get_conversion_rate(from_currency, to_currency, date)
        result = amount * rate
        _logger.info(f"Conversion result: {amount} × {rate} = {result}")
        return result
