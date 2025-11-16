from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CateringPackage(models.Model):
    _name = 'cater.package'
    _description = 'Catering Package'
    _order = 'sequence, name'
    _check_company_auto = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Package Name', required=True, tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        default=lambda self: self.env.company,
        index=True
    )
    
    # Package Details
    description = fields.Html('Description', help="Detailed package description for customers")
    short_description = fields.Text('Short Description', help="Brief summary for listings")
    
    # Package Type and Category
    package_type = fields.Selection([
        ('wedding', 'Wedding Package'),
        ('birthday', 'Birthday Package'),
        ('corporate', 'Corporate Package'),
        ('funeral', 'Funeral Package'),
        ('outdooring', 'Outdooring Package'),
        ('graduation', 'Graduation Package'),
        ('custom', 'Custom Package'),
        ('general', 'General Package')
    ], 'Package Type', required=True, default='general', tracking=True)
    
    category = fields.Selection([
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('deluxe', 'Deluxe'),
        ('custom', 'Custom')
    ], 'Category', default='standard', tracking=True)
    
    # Capacity
    min_guests = fields.Integer('Minimum Guests', default=1)
    max_guests = fields.Integer('Maximum Guests', default=1000)
    
    # Package Contents
    menu_item_ids = fields.Many2many(
        'cater.menu.item',
        'package_menu_rel',
        'package_id',
        'menu_item_id',
        string='Menu Items',
        help="Menu items included in this package"
    )
    service_ids = fields.Many2many(
        'cater.service',
        'package_service_rel',
        'package_id',
        'service_id',
        string='Services',
        help="Services included in this package"
    )
    
    # Package Lines for customizable quantities
    package_menu_line_ids = fields.One2many(
        'cater.package.menu.line',
        'package_id',
        string='Package Menu Items',
        help="Detailed menu items with quantities"
    )
    package_service_line_ids = fields.One2many(
        'cater.package.service.line',
        'package_id',
        string='Package Services',
        help="Detailed services with quantities"
    )
    
    # Pricing
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        default=lambda self: self.env.company.currency_id
    )
    price_per_person = fields.Monetary(
        'Price per Person',
        currency_field='currency_id',
        help="Base price per person"
    )
    fixed_price = fields.Monetary(
        'Fixed Price',
        currency_field='currency_id',
        help="Fixed package price (if not per person)"
    )
    pricing_method = fields.Selection([
        ('per_person', 'Per Person'),
        ('fixed', 'Fixed Price'),
        ('custom', 'Custom Calculation')
    ], 'Pricing Method', default='per_person', required=True, tracking=True)
    
    # Computed Pricing
    menu_total = fields.Monetary(
        'Menu Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    service_total = fields.Monetary(
        'Service Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    estimated_cost = fields.Monetary(
        'Estimated Cost',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help="Total estimated cost for minimum guests"
    )
    
    # Additional Features
    features = fields.Text('Features', help="Key features of this package (one per line)")
    terms_conditions = fields.Text('Terms & Conditions')
    
    # Media
    image = fields.Image('Package Image', max_width=1024, max_height=1024)
    image_medium = fields.Image('Medium Image', related='image', max_width=256, max_height=256, store=True)
    image_small = fields.Image('Small Image', related='image', max_width=128, max_height=128, store=True)
    
    # Availability
    available_from = fields.Date('Available From')
    available_to = fields.Date('Available To')
    is_available = fields.Boolean('Currently Available', compute='_compute_is_available', store=False)
    
    # Booking Statistics
    booking_count = fields.Integer('Bookings', compute='_compute_booking_count')
    
    # Display
    color = fields.Integer('Color Index', default=0)
    
    @api.depends('available_from', 'available_to')
    def _compute_is_available(self):
        today = fields.Date.today()
        for package in self:
            is_available = package.active
            if package.available_from and today < package.available_from:
                is_available = False
            if package.available_to and today > package.available_to:
                is_available = False
            package.is_available = is_available
    
    @api.depends('package_menu_line_ids.subtotal', 'package_service_line_ids.subtotal',
                 'price_per_person', 'fixed_price', 'pricing_method', 'min_guests')
    def _compute_totals(self):
        for package in self:
            menu_total = sum(package.package_menu_line_ids.mapped('subtotal'))
            service_total = sum(package.package_service_line_ids.mapped('subtotal'))
            
            package.menu_total = menu_total
            package.service_total = service_total
            
            if package.pricing_method == 'per_person':
                package.estimated_cost = package.price_per_person * package.min_guests
            elif package.pricing_method == 'fixed':
                package.estimated_cost = package.fixed_price
            else:
                # Custom calculation based on menu and service totals
                package.estimated_cost = menu_total + service_total
    
    def _compute_booking_count(self):
        for package in self:
            package.booking_count = self.env['cater.event.booking'].search_count([
                ('package_id', '=', package.id)
            ])
    
    @api.constrains('min_guests', 'max_guests')
    def _check_guest_limits(self):
        for package in self:
            if package.min_guests < 1:
                raise ValidationError(_('Minimum guests must be at least 1.'))
            if package.max_guests < package.min_guests:
                raise ValidationError(_('Maximum guests cannot be less than minimum guests.'))
    
    @api.constrains('available_from', 'available_to')
    def _check_availability_dates(self):
        for package in self:
            if package.available_from and package.available_to:
                if package.available_to < package.available_from:
                    raise ValidationError(_('Available To date must be after Available From date.'))
    
    def action_view_bookings(self):
        """View all bookings using this package"""
        self.ensure_one()
        return {
            'name': _('Bookings - %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'cater.event.booking',
            'view_mode': 'kanban,list,form',
            'domain': [('package_id', '=', self.id)],
            'context': {
                'default_package_id': self.id,
                'default_event_type': self.package_type if self.package_type != 'general' else False,
            }
        }
    
    def action_duplicate_package(self):
        """Duplicate package with new name"""
        self.ensure_one()
        new_package = self.copy({'name': _('%s (Copy)', self.name)})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cater.package',
            'view_mode': 'form',
            'res_id': new_package.id,
            'target': 'current',
        }
    
    def toggle_active(self):
        """Toggle active state"""
        for package in self:
            package.active = not package.active


class PackageMenuLine(models.Model):
    _name = 'cater.package.menu.line'
    _description = 'Package Menu Line'
    _order = 'sequence, id'
    _check_company_auto = True

    sequence = fields.Integer('Sequence', default=10)
    package_id = fields.Many2one(
        'cater.package',
        'Package',
        required=True,
        ondelete='cascade',
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        related='package_id.company_id',
        store=True,
        index=True
    )
    
    menu_item_id = fields.Many2one(
        'cater.menu.item',
        'Menu Item',
        required=True,
        ondelete='restrict'
    )
    name = fields.Char('Description', related='menu_item_id.name', store=True)
    
    quantity = fields.Float('Quantity', default=1.0, required=True)
    unit_price = fields.Monetary(
        'Unit Price',
        related='menu_item_id.price_per_person',
        currency_field='currency_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='package_id.currency_id',
        store=True
    )
    subtotal = fields.Monetary(
        'Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id'
    )
    
    notes = fields.Text('Notes')
    
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than 0.'))


class PackageServiceLine(models.Model):
    _name = 'cater.package.service.line'
    _description = 'Package Service Line'
    _order = 'sequence, id'
    _check_company_auto = True

    sequence = fields.Integer('Sequence', default=10)
    package_id = fields.Many2one(
        'cater.package',
        'Package',
        required=True,
        ondelete='cascade',
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        related='package_id.company_id',
        store=True,
        index=True
    )
    
    service_id = fields.Many2one(
        'cater.service',
        'Service',
        required=True,
        ondelete='restrict'
    )
    name = fields.Char('Description', related='service_id.name', store=True)
    
    quantity = fields.Float('Quantity', default=1.0, required=True)
    unit_price = fields.Monetary(
        'Unit Price',
        related='service_id.price',
        currency_field='currency_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='package_id.currency_id',
        store=True
    )
    subtotal = fields.Monetary(
        'Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id'
    )
    
    notes = fields.Text('Notes')
    
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than 0.'))
