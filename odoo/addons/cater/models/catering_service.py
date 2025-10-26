from odoo import models, fields, api


class CateringService(models.Model):
    _name = 'cater.service'
    _description = 'Catering Service'
    _order = 'name'

    name = fields.Char('Service Name', required=True)
    description = fields.Text('Description')
    price = fields.Monetary('Price', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)
    service_type = fields.Selection([
        ('equipment', 'Equipment Rental'),
        ('staff', 'Additional Staff'),
        ('decoration', 'Decoration'),
        ('transport', 'Transportation'),
        ('cleanup', 'Cleanup Service'),
        ('other', 'Other')
    ], 'Service Type', required=True)
    duration = fields.Float('Duration (Hours)', default=1.0)
    active = fields.Boolean('Active', default=True)