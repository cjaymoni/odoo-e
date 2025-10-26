from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MenuCategory(models.Model):
    _name = 'cater.menu.category'
    _description = 'Menu Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    image = fields.Image('Category Image')

class MenuItem(models.Model):
    _name = 'cater.menu.item'
    _description = 'Menu Item'
    _order = 'category_id, name'

    name = fields.Char('Item Name', required=True)
    category_id = fields.Many2one('cater.menu.category', 'Category', required=True)
    description = fields.Text('Description')
    price_per_person = fields.Monetary('Price per Person (GHS)', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)
    minimum_order = fields.Integer('Minimum Order Quantity', default=10)
    preparation_time = fields.Float('Preparation Time (Hours)', default=2.0)
    is_vegetarian = fields.Boolean('Vegetarian')
    is_spicy = fields.Boolean('Spicy')
    allergens = fields.Char('Allergens')
    image = fields.Image('Item Image')
    active = fields.Boolean('Active', default=True)
    
    # Availability
    available_from = fields.Datetime('Available From')
    available_to = fields.Datetime('Available To')
    
    @api.constrains('price_per_person')
    def _check_price(self):
        for record in self:
            if record.price_per_person <= 0:
                raise ValidationError("Price must be greater than zero.")
    
    @api.constrains('minimum_order')
    def _check_minimum_order(self):
        for record in self:
            if record.minimum_order < 1:
                raise ValidationError("Minimum order must be at least 1.")
