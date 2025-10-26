
from odoo import models, fields, api, _


class ResPartnerExtend(models.Model):
    _inherit = 'res.partner'

    # Additional fields for catering customers
    is_catering_customer = fields.Boolean('Is Catering Customer', default=False)
    preferred_cuisine = fields.Selection([
        ('ghanaian', 'Ghanaian'),
        ('continental', 'Continental'),
        ('chinese', 'Chinese'),
        ('indian', 'Indian'),
        ('mixed', 'Mixed')
    ], 'Preferred Cuisine')
    
    # Event history
    booking_ids = fields.One2many('cater.event.booking', 'partner_id', 'Bookings')
    booking_count = fields.Integer('Booking Count', compute='_compute_booking_count')
    last_booking_date = fields.Datetime('Last Booking', compute='_compute_last_booking')
    total_spent = fields.Monetary('Total Spent', compute='_compute_total_spent', currency_field='currency_id')
    
    # Communication preferences
    whatsapp_opt_in = fields.Boolean('WhatsApp Notifications', default=True)
    email_opt_in = fields.Boolean('Email Notifications', default=True)
    
    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for partner in self:
            partner.booking_count = len(partner.booking_ids)
    
    @api.depends('booking_ids')
    def _compute_last_booking(self):
        for partner in self:
            if partner.booking_ids:
                partner.last_booking_date = max(partner.booking_ids.mapped('event_date'))
            else:
                partner.last_booking_date = False
    
    @api.depends('booking_ids.total_amount')
    def _compute_total_spent(self):
        for partner in self:
            partner.total_spent = sum(partner.booking_ids.filtered(
                lambda b: b.state in ['confirmed', 'completed']
            ).mapped('total_amount'))
