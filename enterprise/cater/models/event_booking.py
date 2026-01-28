from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from odoo.tools import float_compare
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class EventBooking(models.Model):
    _name = 'cater.event.booking'
    _description = 'Event Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'event_date desc, create_date desc'
    _check_company_auto = True

    def init(self):
        """Create database indexes for performance"""
        super().init()
        # Create indexes using SQL
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_booking_event_date 
            ON cater_event_booking(event_date);
        """)
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_booking_state 
            ON cater_event_booking(state);
        """)
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_booking_partner_state 
            ON cater_event_booking(partner_id, state);
        """)
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_booking_company_id 
            ON cater_event_booking(company_id);
        """)

    # Basic Information
    name = fields.Char('Booking Reference', required=True, copy=False, default='New')
    company_id = fields.Many2one('res.company', 'Company', required=True, 
                                  default=lambda self: self.env.company,
                                  index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True, tracking=True, default=lambda self: self.env.user.partner_id)
    event_name = fields.Char('Event Name', required=True, tracking=True)
    event_type = fields.Selection([
        ('wedding', 'Wedding'),
        ('birthday', 'Birthday Party'),  
        ('corporate', 'Corporate Event'),
        ('funeral', 'Funeral'),
        ('outdooring', 'Outdooring'),
        ('graduation', 'Graduation'),
        ('other', 'Other')
    ], 'Event Type', required=True, tracking=True)
    
    # Date and Location
    event_date = fields.Datetime('Event Date', required=True, tracking=True)
    event_duration = fields.Float('Duration (Hours)', default=4.0, required=True)
    venue = fields.Char('Venue', required=True)
    venue_address = fields.Text('Venue Address')
    guest_count = fields.Integer('Expected Guests', required=True, tracking=True)
    
    # Range Calculation for Overlap Detection
    event_end_date = fields.Datetime('Event End Date', compute='_compute_event_end_date', store=True, index=True)

    @api.depends('event_date', 'event_duration')
    def _compute_event_end_date(self):
        for booking in self:
            if booking.event_date and booking.event_duration:
                booking.event_end_date = booking.event_date + timedelta(hours=booking.event_duration)
            else:
                booking.event_end_date = False
    
    # Package
    package_id = fields.Many2one('cater.package', 'Package', tracking=True, 
                                  help="Select a pre-configured package for this booking")
    
    # Menu and Services
    menu_line_ids = fields.One2many('cater.booking.menu.line', 'booking_id', 'Menu Items')
    service_line_ids = fields.One2many('cater.booking.service.line', 'booking_id', 'Additional Services')
    service_type_group = fields.Selection([
        ('equipment', 'Equipment Rental'),
        ('staff', 'Additional Staff'),
        ('decoration', 'Decoration'),
        ('transport', 'Transportation'),
        ('cleanup', 'Cleanup Service'),
        ('other', 'Other'),
        ('mixed', 'Mixed Services'),
    ], string='Primary Service Type', compute='_compute_service_type_group', store=True, readonly=True,
       help="Helps group bookings by their dominant service type in reporting views.")
    
    # Pricing (removed tracking from computed fields)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)
    menu_total = fields.Monetary('Menu Total', compute='_compute_totals', store=True)
    service_total = fields.Monetary('Service Total', compute='_compute_totals', store=True)
    subtotal = fields.Monetary('Subtotal', compute='_compute_totals', store=True)
    tax_amount = fields.Monetary('VAT (15%)', compute='_compute_totals', store=True)  # Ghana VAT
    total_amount = fields.Monetary('Total Amount', compute='_compute_totals', store=True,
                                   inverse='_inverse_total_amount')
    manual_total_override = fields.Boolean('Manual Total Override', default=False,
                                           help="Enable to lock the total amount to a manually provided value.")
    manual_total_amount = fields.Monetary('Manual Total Amount', currency_field='currency_id')
    
    # Multi-Currency Display (dynamically shows all user-defined currency rates)
    currency_conversion_ids = fields.One2many('cater.booking.currency.conversion', 'booking_id',
                                             string='Currency Conversions',
                                             compute='_compute_currency_conversions',
                                             store=True,
                                             help="Dynamic currency conversions based on user-defined rates")
    show_currency_conversions = fields.Boolean('Show Currency Conversions', default=True,
                                               help="Display currency conversions for all defined rates")
    
    # Payment
    deposit_amount = fields.Monetary('Deposit Required (50%)', compute='_compute_deposit', store=True)
    paid_amount = fields.Monetary('Amount Paid', default=0.0, tracking=True)
    balance_due = fields.Monetary('Balance Due', compute='_compute_balance', store=True,
                                  inverse='_inverse_balance_due')
    
    # Status and Workflow  
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True)
    
    # Kanban color for visual organization
    color = fields.Integer('Color Index', default=0)
    
    # Special Requirements
    special_requests = fields.Text('Special Requests')
    dietary_restrictions = fields.Text('Dietary Restrictions')
    
    # Communication
    whatsapp_sent = fields.Boolean('WhatsApp Notification Sent', default=False)
    last_whatsapp_date = fields.Datetime('Last WhatsApp Sent')
    partner_mobile = fields.Char('Customer Mobile', related='partner_id.mobile', store=False, readonly=False)
    
    # Feedback Tracking
    feedback_request_sent = fields.Boolean('Feedback Request Sent', default=False)
    feedback_request_date = fields.Datetime('Feedback Request Date')
    feedback_received = fields.Boolean('Feedback Received', compute='_compute_feedback_received', store=True)
    feedback_confirmed = fields.Boolean('Feedback Confirmation Sent', default=False)
    
    
    # Related Records
    sale_order_id = fields.Many2one('sale.order', 'Sales Order')
    lead_id = fields.Many2one('crm.lead', 'CRM Lead', readonly=True, 
                              help='CRM Lead that was converted to this booking')
    lead_count = fields.Integer('Lead Count', compute='_compute_lead_count')
    invoice_ids = fields.One2many('account.move', 'catering_booking_id', 'Invoices')
    invoice_count = fields.Integer('Invoice Count', compute='_compute_invoice_count')
    feedback_ids = fields.One2many('cater.feedback', 'booking_id', 'Feedback')
    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for booking in self:
            booking.invoice_count = len(booking.invoice_ids)
    
    @api.depends('lead_id')
    def _compute_lead_count(self):
        """Compute number of related leads"""
        for booking in self:
            booking.lead_count = 1 if booking.lead_id else 0
    
    def _is_filter_active(self, search_key, context_key=None):
        ctx = self.env.context
        return bool((search_key and ctx.get(search_key)) or (context_key and ctx.get(context_key)))

    def _get_dynamic_date_ranges(self):
        today = fields.Date.context_today(self)
        ranges = []

        def add_range(start_date, end_date):
            start_dt = datetime.combine(start_date, time.min)
            end_dt = datetime.combine(end_date, time.max)
            ranges.append((start_dt, end_dt))

        if not today:
            return ranges

        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        if self._is_filter_active('search_default_today', 'cater_filter_today'):
            add_range(today, today)
        if self._is_filter_active('search_default_tomorrow', 'cater_filter_tomorrow'):
            next_day = today + timedelta(days=1)
            add_range(next_day, next_day)
        if self._is_filter_active('search_default_this_week_events', 'cater_filter_this_week'):
            add_range(week_start, week_end)
        if self._is_filter_active('search_default_next_week', 'cater_filter_next_week'):
            next_week_start = week_end + timedelta(days=1)
            next_week_end = next_week_start + timedelta(days=6)
            add_range(next_week_start, next_week_end)
        if self._is_filter_active('search_default_upcoming_bookings', 'cater_filter_next_30'):
            add_range(today, today + timedelta(days=30))
        if self._is_filter_active('search_default_this_month', 'cater_filter_this_month'):
            month_start = today.replace(day=1)
            next_month_start = month_start + relativedelta(months=1)
            month_end = next_month_start - timedelta(days=1)
            add_range(month_start, month_end)

        return ranges

    def _apply_dynamic_date_filters(self, domain):
        ranges = self._get_dynamic_date_ranges()
        if not ranges:
            return domain

        normalized = domain[:] if domain else []
        for start_dt, end_dt in ranges:
            normalized = expression.AND([
                normalized,
                [
                    ('event_date', '>=', fields.Datetime.to_string(start_dt)),
                    ('event_date', '<=', fields.Datetime.to_string(end_dt)),
                ],
            ])
        return normalized

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        domain = self._apply_dynamic_date_filters(domain or [])
        return super()._search(domain, offset=offset, limit=limit, order=order)


    
    @api.depends('feedback_ids')
    def _compute_feedback_received(self):
        for booking in self:
            booking.feedback_received = bool(booking.feedback_ids)
    
    @api.onchange('package_id')
    def _onchange_package_id(self):
        """Populate menu and service lines from selected package"""
        if self.package_id:
            self._apply_package_contents()

    def action_populate_from_package(self):
        """Public method to populate from package, can be called on existing records"""
        self._apply_package_contents()

    def _apply_package_contents(self):
        """Internal helper to apply package items to booking"""
        for booking in self:
            if not booking.package_id:
                continue
            
            # Prepare menu lines
            menu_lines = [(5, 0, 0)]
            for package_line in booking.package_id.package_menu_line_ids:
                menu_lines.append((0, 0, {
                    'menu_item_id': package_line.menu_item_id.id,
                    'quantity': int(package_line.quantity),
                    'notes': package_line.notes or '',
                }))
            
            # Prepare service lines
            service_lines = [(5, 0, 0)]
            for package_line in booking.package_id.package_service_line_ids:
                service_lines.append((0, 0, {
                    'service_id': package_line.service_id.id,
                    'quantity': int(package_line.quantity),
                    'notes': package_line.notes or '',
                }))
            
            vals = {
                'menu_line_ids': menu_lines,
                'service_line_ids': service_lines,
            }
            
            # Set event type if package has specific type
            if booking.package_id.package_type and booking.package_id.package_type != 'general':
                vals['event_type'] = booking.package_id.package_type
                
            booking.write(vals)
    
    @api.depends('menu_line_ids.subtotal', 'service_line_ids.subtotal',
                 'manual_total_override', 'manual_total_amount')
    def _compute_totals(self):
        for booking in self:
            booking.menu_total = sum(booking.menu_line_ids.mapped('subtotal'))
            booking.service_total = sum(booking.service_line_ids.mapped('subtotal'))
            booking.subtotal = booking.menu_total + booking.service_total
            booking.tax_amount = booking.subtotal * 0.15  # Ghana VAT 15%
            computed_total = booking.subtotal + booking.tax_amount
            if booking.manual_total_override:
                booking.total_amount = booking.manual_total_amount or computed_total
            else:
                booking.total_amount = computed_total
                booking.manual_total_amount = False

    @api.depends('service_line_ids.service_id.service_type')
    def _compute_service_type_group(self):
        for booking in self:
            service_types = booking.service_line_ids.mapped('service_id.service_type')
            if not service_types:
                booking.service_type_group = False
            else:
                unique_types = set(filter(None, service_types))
                booking.service_type_group = unique_types.pop() if len(unique_types) == 1 else 'mixed'
    
    @api.depends('total_amount', 'currency_id', 'event_date')
    def _compute_currency_conversions(self):
        """Dynamically convert total amount to all currencies with user-defined rates"""
        for booking in self:
            _logger.info(f"Computing currency conversions for {booking.name}: total={booking.total_amount}, currency={booking.currency_id.name}")
            
            if not booking.total_amount or not booking.currency_id:
                booking.currency_conversion_ids = [(5, 0, 0)]  # Clear all
                _logger.warning(f"Skipping {booking.name}: no total_amount or currency_id")
                continue
            
            booking_currency = booking.currency_id
            conversion_date = booking.event_date.date() if booking.event_date else fields.Date.today()
            
            # Find all currencies that have rates defined for this company
            # Get the most recent rate for each currency
            rate_records = self.env['cater.currency.rate'].search([
                ('company_id', '=', booking.company_id.id),
                ('active', '=', True),
                ('date', '<=', conversion_date)
            ], order='currency_id, date desc')
            
            # Get unique currencies from rate records (most recent rate per currency)
            currencies_with_rates = {}
            seen_currencies = set()
            for rate_record in rate_records:
                currency = rate_record.currency_id
                if currency.id not in seen_currencies:
                    currencies_with_rates[currency.id] = currency
                    seen_currencies.add(currency.id)
            
            # Build conversion lines
            conversion_lines = []
            for currency_id, target_currency in currencies_with_rates.items():
                # Skip if it's the same as booking currency
                if target_currency == booking_currency:
                    continue
                
                # Get conversion rate
                conversion_rate = self.env['cater.currency.rate'].get_conversion_rate(
                    booking_currency,
                    target_currency,
                    conversion_date
                )
                
                if conversion_rate > 0:
                    converted_amount = booking.total_amount * conversion_rate
                    conversion_lines.append((0, 0, {
                        'currency_id': target_currency.id,
                        'converted_amount': converted_amount,
                        'rate_used': conversion_rate,
                    }))
                    _logger.info(f"Added conversion: {booking.total_amount} {booking_currency.name} → {converted_amount} {target_currency.name} (rate: {conversion_rate})")
                else:
                    _logger.warning(f"No rate found for {booking_currency.name} → {target_currency.name} on {conversion_date}")
            
            # Update the One2many field (this will automatically clear old and create new)
            booking.currency_conversion_ids = [(5, 0, 0)] + conversion_lines
    
    
    @api.depends('total_amount')
    def _compute_deposit(self):
        for booking in self:
            booking.deposit_amount = booking.total_amount * 0.5  # 50% deposit
    
    @api.depends('total_amount', 'paid_amount')
    def _compute_balance(self):
        for booking in self:
            booking.balance_due = booking.total_amount - booking.paid_amount

    def _inverse_total_amount(self):
        for booking in self:
            computed_total = booking.subtotal + booking.tax_amount
            currency = booking.currency_id or booking.company_id.currency_id
            rounding = currency.rounding if currency else 0.01
            if float_compare(booking.total_amount, computed_total, precision_rounding=rounding) != 0:
                booking.manual_total_override = True
                booking.manual_total_amount = booking.total_amount
            else:
                booking.manual_total_override = False
                booking.manual_total_amount = False

    def _inverse_balance_due(self):
        for booking in self:
            currency = booking.currency_id or booking.company_id.currency_id
            desired_paid = booking.total_amount - booking.balance_due
            if desired_paid < 0:
                desired_paid = 0.0
            booking.paid_amount = currency.round(desired_paid) if currency else desired_paid
    
    @api.constrains('event_date')
    def _check_event_date(self):
        for booking in self:
            # Allow past dates for completed bookings (historical data/demo)
            if booking.state == 'completed':
                continue
            if booking.event_date <= fields.Datetime.now():
                raise ValidationError("Event date must be in the future.")


    @api.onchange('event_date', 'event_duration')
    def _onchange_event_timing_conflict(self):
        """Provide immediate warning if a timing conflict is detected across any venue"""
        if self.event_date and self.event_duration:
            start_a = self.event_date
            end_a = start_a + timedelta(hours=self.event_duration)
            
            domain = [
                ('state', 'not in', ['cancelled']),
                ('event_date', '<', end_a),
                ('event_end_date', '>', start_a)
            ]
            if self._origin:
                domain.append(('id', '!=', self._origin.id))
                
            overlap = self.search(domain, limit=1)
            if overlap:
                return {
                    'warning': {
                        'title': _("Event Timing Conflict"),
                        'message': _("There is already another event ('%s' at '%s') scheduled for an overlapping period (%s to %s).") % (
                            overlap.event_name or overlap.name,
                            overlap.venue or _("TBD"),
                            overlap.event_date.strftime('%Y-%m-%d %H:%M'),
                            overlap.event_end_date.strftime('%Y-%m-%d %H:%M')
                        )
                    }
                }
    
    @api.constrains('guest_count')
    def _check_guest_count(self):
        for booking in self:
            if booking.guest_count < 1:
                raise ValidationError("Guest count must be at least 1.")
            elif booking.guest_count > 1000:
                raise ValidationError("Guest count cannot exceed 1000 for a single event.")
    
    @api.constrains('paid_amount', 'total_amount')
    def _check_payment_amount(self):
        for booking in self:
            if booking.paid_amount < 0:
                raise ValidationError("Paid amount cannot be negative.")
            if booking.paid_amount > booking.total_amount:
                raise ValidationError("Paid amount cannot exceed total amount.")
    
    @api.constrains('event_duration')
    def _check_event_duration(self):
        for booking in self:
            if booking.event_duration <= 0:
                raise ValidationError("Event duration must be positive.")
            elif booking.event_duration > 24:
                raise ValidationError("Event duration cannot exceed 24 hours.")
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle batch creation and package population"""
        for vals in vals_list:
            # Auto-generate sequence if not provided
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cater.event.booking') or 'New'
            
            # Auto-set catering customer flag
            if 'partner_id' in vals:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                if not partner.is_catering_customer:
                    partner.is_catering_customer = True

            # Systematic Package Population
            # If a package is selected and no lines are explicitly provided, populate them from the package
            package_id = vals.get('package_id')
            has_menu_lines = bool(vals.get('menu_line_ids'))
            has_service_lines = bool(vals.get('service_line_ids'))
            
            _logger.info(f"Creating booking - package_id: {package_id}, has_menu_lines: {has_menu_lines}, has_service_lines: {has_service_lines}")
            
            if package_id:
                package = self.env['cater.package'].browse(package_id)
                if not package.exists():
                    _logger.warning(f"Package {package_id} does not exist")
                else:
                    _logger.info(f"Package found: {package.name}, menu_lines: {len(package.package_menu_line_ids)}, service_lines: {len(package.package_service_line_ids)}")
                    
                    # Always populate from package if no lines are explicitly provided
                    if not has_menu_lines and not has_service_lines:
                        _logger.info(f"Systematically populating from package {package.name} during creation")
                        
                        # Populate menu lines
                        menu_lines = []
                        for line in package.package_menu_line_ids:
                            _logger.info(f"Adding menu item: {line.menu_item_id.name}, quantity: {line.quantity}")
                            menu_lines.append((0, 0, {
                                'menu_item_id': line.menu_item_id.id,
                                'quantity': int(line.quantity),
                                'notes': line.notes or '',
                            }))
                        if menu_lines:
                            vals['menu_line_ids'] = menu_lines
                            _logger.info(f"Added {len(menu_lines)} menu lines to booking")
                        else:
                            _logger.warning(f"Package {package.name} has no menu items")
                        
                        # Populate service lines
                        service_lines = []
                        for line in package.package_service_line_ids:
                            _logger.info(f"Adding service: {line.service_id.name}, quantity: {line.quantity}")
                            service_lines.append((0, 0, {
                                'service_id': line.service_id.id,
                                'quantity': int(line.quantity),
                                'notes': line.notes or '',
                            }))
                        if service_lines:
                            vals['service_line_ids'] = service_lines
                            _logger.info(f"Added {len(service_lines)} service lines to booking")
                        
                        # Set event type if package has specific type and not already set
                        if package.package_type and package.package_type != 'general' and not vals.get('event_type'):
                            vals['event_type'] = package.package_type
                    else:
                        _logger.info(f"Skipping package population - lines already provided")
        
        return super().create(vals_list)
    
    def write(self, vals):
        # Prevent modification of confirmed bookings
        if any(booking.state in ['confirmed', 'in_progress', 'completed'] for booking in self):
            restricted_fields = ['partner_id', 'event_date', 'venue', 'guest_count']
            if any(field in vals for field in restricted_fields) and not self.env.user.has_group('cater.catering_manager_group'):
                raise ValidationError("Only managers can modify confirmed bookings.")
        
        # Clear dashboard cache when booking data changes
        if any(field in vals for field in ['state', 'total_amount', 'create_date']):
            try:
                self.env['cater.dashboard'].clear_dashboard_cache()
            except Exception as e:
                _logger.warning(f"Failed to clear dashboard cache: {e}")
        
        # Disable tracking for computed fields to reduce chatter noise
        computed_fields = ['menu_total', 'service_total', 'subtotal', 'tax_amount', 'total_amount', 'deposit_amount', 'balance_due']
        if any(field in vals for field in computed_fields) and len(vals) == len([f for f in vals if f in computed_fields]):
            # If only computed fields are being updated, disable tracking
            return super(EventBooking, self.with_context(mail_notrack=True)).write(vals)
        
        return super().write(vals)
    
    def action_confirm(self):
        """Confirm the booking and create sale order"""
        if not self.menu_line_ids:
            raise UserError("Please add at least one menu item before confirming.")
        
        self.state = 'confirmed'
        self._create_sale_order()
        self._send_whatsapp_confirmation()
        
        # Log activity
        self.message_post(
            body=f"Booking confirmed for {self.event_name} on {self.event_date.strftime('%Y-%m-%d %H:%M')}",
            message_type='notification'
        )
        self.message_post(body="Booking confirmed", message_type='notification')
    
    def action_start_event(self):
        """Mark event as in progress"""
        self.state = 'in_progress'
        self.message_post(body="Event started", message_type='notification')
    
    def action_complete(self):
        """Complete the event and trigger feedback request"""
        self.state = 'completed'
        self._send_feedback_request()
        self.message_post(body="Event completed successfully", message_type='notification')
    
    def action_cancel(self):
        """Cancel the booking"""
        self.state = 'cancelled'
        self.message_post(body="Booking cancelled", message_type='notification')
    
    def _create_sale_order(self):
        """Create sale order from booking"""
        if self.sale_order_id:
            return
            
        order_lines = []
        
        # Add menu items
        for line in self.menu_line_ids:
            order_lines.append((0, 0, {
                'product_id': self._get_or_create_product(line.menu_item_id.name, line.price_unit).id,
                'product_uom_qty': line.quantity,
                'price_unit': line.price_unit,
            }))
        
        # Add services
        for line in self.service_line_ids:
            order_lines.append((0, 0, {
                'product_id': self._get_or_create_product(line.service_id.name, line.price_unit).id,
                'product_uom_qty': line.quantity,
                'price_unit': line.price_unit,
            }))
        
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_lines,
            'note': f"Event: {self.event_name}\nDate: {self.event_date}\nGuests: {self.guest_count}"
        })
        
        self.sale_order_id = sale_order.id
        return sale_order
    
    def _get_or_create_product(self, name, price):
        """Get or create product for sale order"""
        product = self.env['product.product'].search([('name', '=', name)], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': name,
                'type': 'service',
                'list_price': price,
                'categ_id': self.env.ref('product.product_category_all').id,
            })
        return product
    
    def action_create_invoice(self):
        """Create invoice from booking with Ghana VAT"""
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_("Please set a customer before creating an invoice."))
        
        if not self.menu_line_ids and not self.service_line_ids:
            raise UserError(_("Please add menu items or services before creating an invoice."))
        
        # Get Ghana VAT tax
        ghana_vat = self.env.ref('cater.ghana_vat_sale_15', raise_if_not_found=False)
        if not ghana_vat:
            # Fallback: search for any 15% sales tax
            ghana_vat = self.env['account.tax'].search([
                ('amount', '=', 15.0),
                ('type_tax_use', '=', 'sale'),
                ('active', '=', True)
            ], limit=1)
        
        invoice_lines = []
        
        # Add menu items
        for line in self.menu_line_ids:
            invoice_line = {
                'name': f"{line.menu_item_id.name} - {self.event_name}",
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, ghana_vat.ids)] if ghana_vat else [],
            }
            invoice_lines.append((0, 0, invoice_line))
        
        # Add services
        for line in self.service_line_ids:
            invoice_line = {
                'name': f"{line.service_id.name} - {self.event_name}",
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, ghana_vat.ids)] if ghana_vat else [],
            }
            invoice_lines.append((0, 0, invoice_line))
        
        # Create invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=30),
            'catering_booking_id': self.id,
            'invoice_line_ids': invoice_lines,
            'narration': f"Event: {self.event_name}\nDate: {self.event_date.strftime('%Y-%m-%d %H:%M') if self.event_date else 'TBD'}\nGuests: {self.guest_count}\nVenue: {self.venue}"
        })
        
        # Post message on booking
        self.message_post(
            body=f"Invoice <a href='/web#id={invoice.id}&model=account.move'>{invoice.name}</a> created",
            message_type='notification'
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
        }
    
    def action_view_invoices(self):
        """View invoices related to this booking"""
        self.ensure_one()
        tree_view = self.env.ref('account.view_move_tree', False)
        form_view = self.env.ref('account.view_move_form', False)
        views = []
        if tree_view:
            views.append((tree_view.id, 'list'))
        if form_view:
            views.append((form_view.id, 'form'))
        # Fallback: if no views found, use view_mode only (Odoo will use default views)
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'domain': [('catering_booking_id', '=', self.id)],
            'context': {'default_catering_booking_id': self.id},
        }
        if views:
            action['view_mode'] = 'list,form'
            action['views'] = views
        else:
            action['view_mode'] = 'list,form'
        return action
    
    def action_view_lead(self):
        """View related CRM lead"""
        self.ensure_one()
        if not self.lead_id:
            raise UserError(_('This booking was not created from a CRM lead.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('CRM Lead'),
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _send_whatsapp_confirmation(self):
        """Send WhatsApp confirmation message if opted in"""
        if not self.partner_id.whatsapp_opt_in:
            _logger.info(f"WhatsApp not sent: {self.partner_id.name} has opted out.")
            return
        try:
            whatsapp_service = self.env['cater.whatsapp.service'].search([('active', '=', True)], limit=1)
            if not whatsapp_service:
                _logger.warning("No active WhatsApp service configured; skipping confirmation send.")
                return
            message = f"""
🎉 *Booking Confirmed!*

Hello {self.partner_id.name},

Your booking for *{self.event_name}* has been confirmed!

📅 *Event Details:*
• Date: {self.event_date.strftime('%A, %B %d, %Y at %I:%M %p')}
• Venue: {self.venue}
• Guests: {self.guest_count}
• Total: GHS {self.total_amount:,.2f}

We're excited to cater your special event! 🍽️

_Thank you for choosing our catering services._
            """
            if whatsapp_service.send_message(self.partner_id.mobile, message.strip()):
                self.whatsapp_sent = True
                self.last_whatsapp_date = fields.Datetime.now()
        except Exception as e:
            _logger.error(f"Failed to send WhatsApp confirmation: {str(e)}")
    
    def _send_feedback_request(self):
        """Send feedback request via WhatsApp if opted in"""
        if not self.partner_id.whatsapp_opt_in:
            _logger.info(f"Feedback WhatsApp not sent: {self.partner_id.name} has opted out.")
            return
        try:
            whatsapp_service = self.env['cater.whatsapp.service'].search([('active', '=', True)], limit=1)
            if not whatsapp_service:
                _logger.warning("No active WhatsApp service configured; skipping feedback send.")
                return
            
            # Simplified, user-friendly template with structured example
            message = f"""✨ *We value your feedback!*

Hello {self.partner_id.name}, 

Thank you for choosing us for your event: *{self.event_name}* (Ref: {self.name}).

We hope you enjoyed our service! Could you please take a moment to rate your experience?

⭐ *Quick Rating:* Reply with a number from 1 to 5.

📊 *Detailed Feedback:* 
booking id: {self.name}
Food Quality (1-5) : 5
Service (1-5) : 5
Presentation (1-5) : 5
Timeliness (1-5) : 5
Comments: Your comments here

Your feedback helps us serve you better! 🙏"""
            
            # Send feedback request and log it
            success = whatsapp_service.send_message(self.partner_id.mobile, message.strip())
            if success:
                # Mark that feedback request was sent
                self.write({'feedback_request_sent': True, 'feedback_request_date': fields.Datetime.now()})
                _logger.info(f"Feedback request sent for booking {self.name} to {self.partner_id.name}")
            
        except Exception as e:
            _logger.error(f"Failed to send feedback request: {str(e)}")
    
    @api.model
    def _cron_send_event_reminders(self):
        """Cron job to send event reminders 24 hours before the event - Optimized"""
        from datetime import timedelta
        import logging
        _logger = logging.getLogger(__name__)
        
        tomorrow = fields.Datetime.now() + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Batch process bookings to avoid memory issues
        batch_size = 50
        offset = 0
        
        while True:
            upcoming_bookings = self.search([
                ('event_date', '>=', tomorrow_start),
                ('event_date', '<=', tomorrow_end),
                ('state', 'in', ['confirmed', 'in_progress']),
                ('partner_id.whatsapp_opt_in', '=', True)  # Only opted-in customers
            ], limit=batch_size, offset=offset)
            
            if not upcoming_bookings:
                break
                
            for booking in upcoming_bookings:
                try:
                    booking._send_whatsapp_confirmation()
                    # Commit after each successful send to avoid losing progress
                    self.env.cr.commit()
                except Exception as e:
                    _logger.warning(f"Failed to send reminder for booking {booking.name}: {e}")
                    # Continue with next booking on error
                    continue
            
            offset += batch_size
    
    @api.model
    def _cron_send_feedback_requests(self):
        """Cron job to send feedback requests for completed events - Optimized"""
        from datetime import timedelta
        import logging
        _logger = logging.getLogger(__name__)
        
        # Look for events completed in the last 24 hours without feedback request sent
        yesterday = fields.Datetime.now() - timedelta(days=1)
        today = fields.Datetime.now()
        
        # Batch process to avoid memory issues
        batch_size = 30
        offset = 0
        
        while True:
            completed_bookings = self.search([
                ('state', '=', 'completed'),
                ('write_date', '>=', yesterday),  # Recently completed
                ('write_date', '<', today),
                ('feedback_request_sent', '=', False),  # No feedback request sent yet
                ('partner_id.whatsapp_opt_in', '=', True)  # Only opted-in customers
            ], limit=batch_size, offset=offset)
            
            if not completed_bookings:
                break
                
            for booking in completed_bookings:
                try:
                    booking._send_feedback_request()
                    # Commit after each successful send
                    self.env.cr.commit()
                except Exception as e:
                    _logger.warning(f"Failed to send feedback request for booking {booking.name}: {e}")
                    continue
            
            offset += batch_size
            
        _logger.info(f"Completed feedback request batch processing")
    
    @api.model
    def _process_whatsapp_feedback_response(self, from_number, message_body):
        """Process WhatsApp feedback response and create feedback record.
        Uses a hybrid matching strategy:
        1. Explicit Booking Reference in message
        2. Direct Mobile Lookup + Recency Ranking
        """
        try:
            _logger.info(f"Processing feedback from {from_number}: '{message_body}'")
            
            # Parse feedback from message first to see if it contains a booking reference
            details = self._parse_feedback_message(message_body)
            rating = details.get('rating')
            comments = details.get('comments')
            booking_ref = details.get('booking_id')
            
            _logger.info(f"Parsed details: {details}")
            
            target_booking = None
            if booking_ref:
                # Search for booking with this name and sender's phone number
                target_booking = self.search([
                    ('name', '=', booking_ref),
                    ('partner_id.mobile', '=', from_number)
                ], limit=1)
                if target_booking:
                    _logger.info(f"Matched booking {target_booking.name} via explicit reference")
            
            # 2. Fallback to Direct Mobile Lookup + Recency Ranking
            if not target_booking:
                _logger.info(f"No booking found by reference, falling back to recency matching for {from_number}")
                target_booking = self.search([
                    ('partner_id.mobile', '=', from_number),
                    ('state', '=', 'completed'),
                    ('feedback_request_sent', '=', True),
                    ('feedback_received', '=', False)
                ], order='feedback_request_date desc', limit=1)

            if not target_booking:
                _logger.info(f"No pending feedback booking found for mobile: {from_number}")
                return False
            
            partner = target_booking.partner_id
            _logger.info(f"Matched booking: {target_booking.name} for partner: {partner.name}")
            
            if rating:
                # Create feedback record
                feedback_vals = {
                    'booking_id': target_booking.id,
                    'partner_id': partner.id,
                    'rating': str(rating),
                    'comments': comments,
                    'source': 'whatsapp',
                    # Use specific ratings if available, otherwise fall back to overall rating
                    'food_quality': details.get('food_quality') or rating,
                    'service_quality': details.get('service_quality') or rating,
                    'presentation': details.get('presentation') or rating,
                    'timeliness': details.get('timeliness') or rating,
                }
                
                feedback = self.env['cater.feedback'].create(feedback_vals)
                
                _logger.info(f"Created feedback {feedback.id} from WhatsApp response")
                
                # Send immediate confirmation
                self._send_feedback_confirmation(from_number, rating, feedback)
                
                # Mark that feedback was received and confirmed
                target_booking.write({
                    'feedback_received': True,
                    'feedback_confirmed': True
                })
                
                # If negative feedback, create follow-up activity
                if rating < 4:
                    self._create_followup_activity(feedback)
                
                return feedback
            else:
                _logger.info(f"Could not parse rating from message: '{message_body}'")
                
        except Exception as e:
            _logger.error(f"Error processing WhatsApp feedback response: {str(e)}")
            import traceback
            _logger.error(f"Traceback: {traceback.format_exc()}")
            
        return False
    
    @api.model
    def _parse_feedback_message(self, message_body):
        """Parse rating and comments from WhatsApp message, supporting structured detailed format"""
        import re
        
        details = {
            'rating': None,
            'comments': message_body.strip(),
            'booking_id': None,
            'food_quality': None,
            'service_quality': None,
            'presentation': None,
            'timeliness': None,
        }
        
        message = message_body.lower().strip()
        
        # 1. Check for structured detailed feedback format
        # booking id: BKxxxxx
        # Food Quality (1-5): 5
        # Service (1-5): 5
        # ...
        
        patterns = {
            'booking_id': r'booking\s*id\s*:\s*(BK\d{5})',
            'food_quality': r'food\s*quality\s*\(1-5\)\s*:\s*(\d)',
            'service_quality': r'service\s*\(1-5\)\s*:\s*(\d)',
            'presentation': r'presentation\s*\(1-5\)\s*:\s*(\d)',
            'timeliness': r'timeliness\s*\(1-5\)\s*:\s*(\d)',
            'comments': r'comments\s*:\s*(.*)',
        }
        
        found_structured = False
        for key, pattern in patterns.items():
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if key in ['food_quality', 'service_quality', 'presentation', 'timeliness']:
                    details[key] = int(val) if 1 <= int(val) <= 5 else None
                else:
                    details[key] = val
                found_structured = True

        if found_structured:
            # If we have structured data, calculate an average or use the first available rating as overall
            ratings = [details[k] for k in ['food_quality', 'service_quality', 'presentation', 'timeliness'] if details[k]]
            if ratings:
                details['rating'] = round(sum(ratings) / len(ratings))
            return details

        # 2. Traditional parsing logic for unstructured messages
        # ... (rest of the manual/sentiment logic)
        
        # Check for explicit booking ref anywhere
        ref_match = re.search(r'BK\d{5}', message_body)
        if ref_match:
            details['booking_id'] = ref_match.group(0)

        rating = None
        # Enhanced rating patterns
        rating_patterns = [
            r'^(\d)\s*[-\s]',        # "5 - excellent"
            r'(\d)\s*star',          # "5 stars"
            r'(\d)/5',               # "4/5"
            r'rating:?\s*(\d)',      # "rating: 4"
            r'(\d)\s*out\s*of\s*5',  # "4 out of 5"
        ]
        
        # Check for explicit rating at start
        explicit_match = re.match(r'^(\d)', message)
        if explicit_match:
            val = int(explicit_match.group(1))
            if 1 <= val <= 5:
                rating = val
                details['comments'] = message_body[1:].strip(' -,.')
        
        if not rating:
            for pattern in rating_patterns:
                match = re.search(pattern, message)
                if match:
                    val = int(match.group(1))
                    if 1 <= val <= 5:
                        rating = val
                        details['comments'] = re.sub(pattern, '', message_body.strip(), flags=re.IGNORECASE).strip(' -,.')
                        break
        
        # Sentiment fallback
        if not rating:
            excellent_words = ['excellent', 'amazing', 'perfect', 'outstanding', 'fantastic']
            very_good_words = ['great', 'awesome', 'lovely', 'delicious']
            if any(word in message for word in excellent_words):
                rating = 5
            elif any(word in message for word in very_good_words):
                rating = 4
            elif 'good' in message:
                rating = 3
            elif any(word in message for word in ['poor', 'bad']):
                rating = 2
            elif any(word in message for word in ['terrible', 'awful']):
                rating = 1
            else:
                rating = 3

        details['rating'] = rating
        return details
    
    def _send_feedback_confirmation(self, mobile_number, rating, feedback):
        """Send a polite sign-off note after feedback receipt"""
        try:
            whatsapp_service = self.env['cater.whatsapp.service'].search([('active', '=', True)], limit=1)
            if not whatsapp_service:
                return
            
            message = f"""✅ *Feedback Recorded*

Thank you for sharing your experience with us! Your {rating}-star rating has been received.

We appreciate your business and look forward to serving you again soon. Have a wonderful day! 🙏

---
_Internal Ref: #FB{feedback.id:04d}_"""
            
            whatsapp_service.send_message(mobile_number, message.strip())
            _logger.info(f"Simplified feedback sign-off sent for booking {self.name}")
            
        except Exception as e:
            _logger.error(f"Failed to send feedback sign-off: {str(e)}")

    def _create_followup_activity(self, feedback):
        """Create follow-up activity for negative feedback"""
        try:
            # Create activity for management follow-up
            activity_vals = {
                'activity_type_id': self.env.ref('mail.mail_activity_data_call').id,
                'summary': f"URGENT: Follow up on {feedback.rating}-star feedback",
                'note': f"""
                <p><strong>Low Rating Alert:</strong> {feedback.rating}/5 stars</p>
                <p><strong>Booking:</strong> {self.name} - {self.event_name}</p>
                <p><strong>Customer:</strong> {self.partner_id.name} ({self.partner_id.mobile})</p>
                <p><strong>Event Date:</strong> {self.event_date}</p>
                <p><strong>Comments:</strong> {feedback.comments or 'No comments provided'}</p>
                <p><strong>Action Required:</strong> Contact customer within 24 hours to address concerns and offer resolution.</p>
                """,
                'res_id': self.id,
                'res_model_id': self.env.ref('cater.model_cater_event_booking').id,
                'user_id': self.env.ref('base.user_admin').id,  # Assign to admin
                'date_deadline': fields.Date.today() + timedelta(days=1)
            }
            
            activity = self.env['mail.activity'].create(activity_vals)
            _logger.info(f"Created follow-up activity {activity.id} for negative feedback {feedback.id}")
            
        except Exception as e:
            _logger.error(f"Failed to create follow-up activity: {str(e)}")

    def _send_feedback_thank_you(self, mobile_number, rating):
        """Send thank you message for feedback (DEPRECATED - Use _send_feedback_confirmation instead)"""
        try:
            whatsapp_service = self.env['cater.whatsapp.service'].search([('active', '=', True)], limit=1)
            if not whatsapp_service:
                return
            
            if rating >= 4:
                message = """
🙏 Thank you for your wonderful feedback!

We're delighted that you enjoyed our catering service. Your satisfaction is our top priority!

Would you mind leaving us a review on Google? It would mean the world to us! 🌟

_We look forward to serving you again soon._
                """.strip()
            else:
                message = """
🙏 Thank you for your feedback.

We appreciate you taking the time to share your experience. We're always working to improve our service.

Our manager will be in touch to discuss your concerns and ensure your next experience exceeds expectations.

_Thank you for choosing our catering services._
                """.strip()
            
            whatsapp_service.send_message(mobile_number, message)
            
        except Exception as e:
            _logger.error(f"Failed to send feedback thank you: {str(e)}")

    @api.model
    def get_feedback_analytics(self, days=30):
        """Get comprehensive feedback analytics for dashboard"""
        from datetime import timedelta
        
        date_from = fields.Datetime.now() - timedelta(days=days)
        
        # Get completed bookings in the period
        domain = [
            ('state', '=', 'completed'),
            ('event_date', '>=', date_from)
        ]
        
        completed_bookings = self.search(domain)
        feedback_requested = completed_bookings.filtered('feedback_request_sent')
        feedback_received = completed_bookings.filtered('feedback_received')
        
        # Calculate response rate
        response_rate = 0
        if feedback_requested:
            response_rate = (len(feedback_received) / len(feedback_requested)) * 100
        
        # Get feedback statistics
        feedback_records = self.env['cater.feedback'].search([
            ('booking_id', 'in', completed_bookings.ids)
        ])
        
        analytics = {
            'period_days': days,
            'completed_bookings': len(completed_bookings),
            'feedback_requests_sent': len(feedback_requested),
            'feedback_received_count': len(feedback_received),
            'response_rate': round(response_rate, 1),
            'pending_feedback': len(feedback_requested) - len(feedback_received),
        }
        
        if feedback_records:
            ratings = [int(f.rating) for f in feedback_records if f.rating]
            if ratings:
                analytics.update({
                    'average_rating': round(sum(ratings) / len(ratings), 2),
                    'five_star_count': len([r for r in ratings if r == 5]),
                    'four_star_count': len([r for r in ratings if r == 4]),
                    'three_star_count': len([r for r in ratings if r == 3]),
                    'two_star_count': len([r for r in ratings if r == 2]),
                    'one_star_count': len([r for r in ratings if r == 1]),
                    'positive_feedback_rate': round((len([r for r in ratings if r >= 4]) / len(ratings)) * 100, 1),
                    'needs_followup': len([r for r in ratings if r < 4]),
                })
        
        return analytics

    @api.model
    def get_feedback_response_analytics(self, days=30):
        """Get detailed feedback response analytics"""
        from datetime import timedelta
        
        date_from = fields.Datetime.now() - timedelta(days=days)
        
        # Get all bookings in the period
        domain = [
            ('state', '=', 'completed'),
            ('event_date', '>=', date_from)
        ]
        
        completed_bookings = self.search(domain)
        
        # Categorize bookings
        feedback_sent = completed_bookings.filtered('feedback_request_sent')
        feedback_received = completed_bookings.filtered('feedback_received')
        feedback_confirmed = completed_bookings.filtered('feedback_confirmed')
        
        # Calculate metrics
        total_completed = len(completed_bookings)
        request_rate = (len(feedback_sent) / total_completed * 100) if total_completed else 0
        response_rate = (len(feedback_received) / len(feedback_sent) * 100) if feedback_sent else 0
        confirmation_rate = (len(feedback_confirmed) / len(feedback_received) * 100) if feedback_received else 0
        
        # Get feedback details
        feedback_records = self.env['cater.feedback'].search([
            ('booking_id', 'in', completed_bookings.ids)
        ])
        
        # Analyze response patterns
        whatsapp_responses = feedback_records.filtered(lambda f: f.source == 'whatsapp')
        avg_response_time = 0
        
        if whatsapp_responses:
            response_times = []
            for feedback in whatsapp_responses:
                if feedback.booking_id.feedback_request_date:
                    time_diff = feedback.feedback_date - feedback.booking_id.feedback_request_date
                    response_times.append(time_diff.total_seconds() / 3600)  # Convert to hours
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Rating distribution
        rating_dist = {}
        for i in range(1, 6):
            rating_dist[f'{i}_star'] = len(feedback_records.filtered(lambda f: f.rating == str(i)))
        
        return {
            'period_days': days,
            'total_completed_bookings': total_completed,
            'feedback_requests_sent': len(feedback_sent),
            'feedback_received_count': len(feedback_received),
            'feedback_confirmed_count': len(feedback_confirmed),
            'request_rate': round(request_rate, 1),
            'response_rate': round(response_rate, 1),
            'confirmation_rate': round(confirmation_rate, 1),
            'avg_response_time_hours': round(avg_response_time, 2),
            'total_feedback': len(feedback_records),
            'whatsapp_feedback': len(whatsapp_responses),
            'rating_distribution': rating_dist,
            'high_ratings_count': len(feedback_records.filtered(lambda f: int(f.rating) >= 4)),
            'needs_followup': len(feedback_records.filtered(lambda f: int(f.rating) < 4)),
        }


class BookingMenuLine(models.Model):
    _name = 'cater.booking.menu.line'
    _description = 'Booking Menu Line'
    _check_company_auto = True

    booking_id = fields.Many2one('cater.event.booking', 'Booking', required=True, ondelete='cascade', check_company=True)
    company_id = fields.Many2one('res.company', 'Company', related='booking_id.company_id', store=True, index=True)
    menu_item_id = fields.Many2one('cater.menu.item', 'Menu Item', required=True, check_company=True)
    quantity = fields.Integer('Quantity (Portions)', required=True, default=1)
    price_unit = fields.Monetary('Unit Price', related='menu_item_id.price_per_person', store=True)
    currency_id = fields.Many2one('res.currency', related='booking_id.currency_id')
    subtotal = fields.Monetary('Subtotal', compute='_compute_subtotal', store=True)
    notes = fields.Char('Special Notes')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity < 1:
                raise ValidationError("Quantity must be at least 1.")
            if line.quantity < line.menu_item_id.minimum_order:
                raise ValidationError(f"Minimum order for {line.menu_item_id.name} is {line.menu_item_id.minimum_order}.")

class BookingServiceLine(models.Model):
    _name = 'cater.booking.service.line'
    _description = 'Booking Service Line'
    _check_company_auto = True

    booking_id = fields.Many2one('cater.event.booking', 'Booking', required=True, ondelete='cascade', check_company=True)
    company_id = fields.Many2one('res.company', 'Company', related='booking_id.company_id', store=True, index=True)
    service_id = fields.Many2one('cater.service', 'Service', required=True, check_company=True)
    quantity = fields.Integer('Quantity', required=True, default=1)
    price_unit = fields.Monetary('Unit Price', related='service_id.price', store=True)
    currency_id = fields.Many2one('res.currency', related='booking_id.currency_id')
    subtotal = fields.Monetary('Subtotal', compute='_compute_subtotal', store=True)
    notes = fields.Char('Special Notes')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit


class BookingCurrencyConversion(models.Model):
    _name = 'cater.booking.currency.conversion'
    _description = 'Booking Currency Conversion'
    _order = 'currency_id'
    _check_company_auto = True

    booking_id = fields.Many2one('cater.event.booking', 'Booking', required=True, ondelete='cascade', check_company=True)
    company_id = fields.Many2one('res.company', 'Company', related='booking_id.company_id', store=True, index=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    converted_amount = fields.Monetary('Converted Amount', required=True, currency_field='currency_id')
    rate_used = fields.Float('Rate Used', digits=(12, 6), required=True,
                             help="Exchange rate used for this conversion")
    
    @api.depends('currency_id')
    def _compute_display_name(self):
        for record in self:
            if record.currency_id:
                record.display_name = f"{record.currency_id.name} Conversion"
            else:
                record.display_name = 'Currency Conversion'
    
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
