


from odoo import models, fields, api


class AccountMoveExtend(models.Model):
    _inherit = 'account.move'

    # Link to catering booking
    catering_booking_id = fields.Many2one('cater.event.booking', 'Catering Booking')
    
    # Additional fields for catering invoices
    event_date = fields.Datetime('Event Date', related='catering_booking_id.event_date', store=True)
    event_name = fields.Char('Event Name', related='catering_booking_id.event_name', store=True)
    guest_count = fields.Integer('Guest Count', related='catering_booking_id.guest_count', store=True)
