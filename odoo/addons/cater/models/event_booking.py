from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class EventBooking(models.Model):
    _name = 'cater.event.booking'
    _description = 'Event Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'event_date desc, create_date desc'

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

    # Basic Information
    name = fields.Char('Booking Reference', required=True, copy=False, default='New')
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
    
    # Menu and Services
    menu_line_ids = fields.One2many('cater.booking.menu.line', 'booking_id', 'Menu Items')
    service_line_ids = fields.One2many('cater.booking.service.line', 'booking_id', 'Additional Services')
    
    # Pricing (removed tracking from computed fields)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)
    menu_total = fields.Monetary('Menu Total', compute='_compute_totals', store=True)
    service_total = fields.Monetary('Service Total', compute='_compute_totals', store=True)
    subtotal = fields.Monetary('Subtotal', compute='_compute_totals', store=True)
    tax_amount = fields.Monetary('VAT (15%)', compute='_compute_totals', store=True)  # Ghana VAT
    total_amount = fields.Monetary('Total Amount', compute='_compute_totals', store=True)
    
    # Payment
    deposit_amount = fields.Monetary('Deposit Required (50%)', compute='_compute_deposit', store=True)
    paid_amount = fields.Monetary('Amount Paid', default=0.0, tracking=True)
    balance_due = fields.Monetary('Balance Due', compute='_compute_balance', store=True)
    
    # Status and Workflow  
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True)
    
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
    invoice_ids = fields.One2many('account.move', 'catering_booking_id', 'Invoices')
    feedback_ids = fields.One2many('cater.feedback', 'booking_id', 'Feedback')
    

    
    @api.depends('feedback_ids')
    def _compute_feedback_received(self):
        for booking in self:
            booking.feedback_received = bool(booking.feedback_ids)
    
    @api.depends('menu_line_ids.subtotal', 'service_line_ids.subtotal')
    def _compute_totals(self):
        for booking in self:
            booking.menu_total = sum(booking.menu_line_ids.mapped('subtotal'))
            booking.service_total = sum(booking.service_line_ids.mapped('subtotal'))
            booking.subtotal = booking.menu_total + booking.service_total
            booking.tax_amount = booking.subtotal * 0.15  # Ghana VAT 15%
            booking.total_amount = booking.subtotal + booking.tax_amount
    
    def write(self, vals):
        # Disable tracking for computed fields to reduce chatter noise
        computed_fields = ['menu_total', 'service_total', 'subtotal', 'tax_amount', 'total_amount', 'deposit_amount', 'balance_due']
        if any(field in vals for field in computed_fields) and len(vals) == len([f for f in vals if f in computed_fields]):
            # If only computed fields are being updated, disable tracking
            return super(EventBooking, self.with_context(mail_notrack=True)).write(vals)
        return super().write(vals)
    
    @api.depends('total_amount')
    def _compute_deposit(self):
        for booking in self:
            booking.deposit_amount = booking.total_amount * 0.5  # 50% deposit
    
    @api.depends('total_amount', 'paid_amount')
    def _compute_balance(self):
        for booking in self:
            booking.balance_due = booking.total_amount - booking.paid_amount
    
    @api.constrains('event_date')
    def _check_event_date(self):
        for booking in self:
            # Allow past dates for completed bookings (historical data/demo)
            if booking.state == 'completed':
                continue
            if booking.event_date <= fields.Datetime.now():
                raise ValidationError("Event date must be in the future.")

    @api.constrains('event_date', 'venue')
    def _check_venue_conflict(self):
        for booking in self:
            if not booking.event_date or not booking.venue:
                continue
            # Find overlapping bookings at the same venue (excluding self)
            overlap = self.search([
                ('id', '!=', booking.id),
                ('venue', '=', booking.venue),
                ('event_date', '=', booking.event_date),
                ('state', 'in', ['confirmed', 'in_progress'])
            ])
            if overlap:
                raise ValidationError(f"Venue '{booking.venue}' is already booked for {booking.event_date}.")
    
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
        """Override create to handle batch creation properly"""
        for vals in vals_list:
            # Auto-generate sequence if not provided
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cater.event.booking') or 'New'
            
            # Auto-set catering customer flag
            if 'partner_id' in vals:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                if not partner.is_catering_customer:
                    partner.is_catering_customer = True
        
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
        self._send_whatsapp_confirmation()
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
            
            # Create more engaging and comprehensive feedback request
            message = f"""🎉 *Booking Confirmed!*

Hello {self.partner_id.name},

Your booking for *{self.event_name}* has been confirmed! 

📅 *Event Details:*
• Date: {self.event_date.strftime('%A, %B %d, %Y at %I:%M %p') if self.event_date else 'TBD'}
• Venue: {self.venue or 'To be confirmed'}
• Guests: {self.guest_count}
• Total: {self.currency_id.symbol if self.currency_id else ''}{'%.2f' % self.total_amount}

We're excited to cater your special event! 🍽️

_Thank you for choosing our catering services._

----

How was your experience with *{self.event_name}*?

🌟 *Please rate our service:*

*Quick Rating:* Reply with just a number (1-5)
⭐ 1 = Poor
⭐⭐ 2 = Fair  
⭐⭐⭐ 3 = Good
⭐⭐⭐⭐ 4 = Very Good
⭐⭐⭐⭐⭐ 5 = Excellent

*Or detailed feedback:*
Rate our:
• Food Quality (1-5)
• Service (1-5) 
• Presentation (1-5)
• Timeliness (1-5)
• Comments

*Example:* "5 - Food was amazing, service excellent, very happy!"

Your feedback helps us serve you better! 💬
            """
            
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
        """Process WhatsApp feedback response and create feedback record"""
        try:
            _logger.info(f"Processing feedback from {from_number}: '{message_body}'")
            
            # Find customer by mobile number
            partner = self.env['res.partner'].search([
                ('mobile', '=', from_number),
                ('is_catering_customer', '=', True)
            ], limit=1)
            
            if not partner:
                _logger.info(f"No customer found for mobile number: {from_number}")
                # Try without is_catering_customer filter
                partner = self.env['res.partner'].search([
                    ('mobile', '=', from_number)
                ], limit=1)
                if partner:
                    _logger.info(f"Found partner {partner.name} but not marked as catering customer")
                return False
            
            _logger.info(f"Found customer: {partner.name} (ID: {partner.id})")
            
            # Find recent completed booking without feedback
            recent_booking = self.search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'completed'),
                ('feedback_ids', '=', False),
                ('event_date', '>=', fields.Datetime.now() - timedelta(days=7))
            ], order='event_date desc', limit=1)
            
            if not recent_booking:
                _logger.info(f"No recent completed booking found for customer: {partner.name}")
                # Check if there are any completed bookings at all
                all_completed = self.search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'completed')
                ], order='event_date desc', limit=5)
                _logger.info(f"Customer has {len(all_completed)} completed bookings total")
                return False
            
            _logger.info(f"Found recent booking: {recent_booking.name} - {recent_booking.event_name}")
            
            # Parse feedback from message
            rating, comments = self._parse_feedback_message(message_body)
            _logger.info(f"Parsed rating: {rating}, comments: '{comments}'")
            
            if rating:
                # Create feedback record
                feedback = self.env['cater.feedback'].create({
                    'booking_id': recent_booking.id,
                    'rating': str(rating),
                    'comments': comments,
                    'source': 'whatsapp',
                    'food_quality': rating,
                    'service_quality': rating,
                    'presentation': rating,
                    'timeliness': rating,
                })
                
                _logger.info(f"Created feedback {feedback.id} from WhatsApp response")
                
                # Send immediate confirmation
                self._send_feedback_confirmation(partner.mobile, rating, feedback)
                
                # Mark that feedback was received and confirmed
                recent_booking.write({
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
        """Parse rating and comments from WhatsApp message"""
        import re
        
        message = message_body.lower().strip()
        rating = None
        comments = message_body.strip()
        
        # Enhanced rating patterns to match real customer responses
        rating_patterns = [
            r'^(\d)\s*[-\s]',        # "5 - excellent", "4 good" (most common)
            r'(\d)\s*star',          # "5 stars", "3 star"
            r'(\d)/5',               # "4/5", "5/5"
            r'rating:?\s*(\d)',      # "rating: 4", "rating 5"
            r'(\d)\s*out\s*of\s*5',  # "4 out of 5"
            r'rate[:\s]*(\d)',       # "rate: 5", "rate 4"
            r'score[:\s]*(\d)',      # "score: 5", "score 4"
            r'give[:\s]*(\d)',       # "give 5", "give: 4"
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, message)
            if match:
                rating_value = int(match.group(1))
                if 1 <= rating_value <= 5:
                    rating = rating_value
                    # Clean comments by removing the rating part
                    comments = re.sub(pattern, '', message_body.strip()).strip(' -,.')
                    break
        
        # Enhanced sentiment analysis for better inference
        if not rating:
            # Highly positive words
            excellent_words = ['excellent', 'amazing', 'perfect', 'outstanding', 'fantastic', 'exceptional', 'superb', 'wonderful', 'magnificent', 'brilliant']
            # Very positive words
            very_good_words = ['great', 'awesome', 'lovely', 'beautiful', 'impressive', 'delicious', 'tasty', 'pleased', 'satisfied', 'happy']
            # Positive words
            good_words = ['good', 'nice', 'fine', 'okay', 'satisfactory', 'decent', 'pleasant', 'alright']
            # Negative words
            poor_words = ['poor', 'bad', 'disappointing', 'unsatisfactory', 'below average']
            # Very negative words
            terrible_words = ['terrible', 'awful', 'horrible', 'disgusting', 'worst', 'hate', 'appalling']
            
            if any(word in message for word in excellent_words):
                rating = 5
            elif any(word in message for word in very_good_words):
                rating = 4  
            elif any(word in message for word in good_words):
                rating = 3
            elif any(word in message for word in poor_words):
                rating = 2
            elif any(word in message for word in terrible_words):
                rating = 1
            else:
                rating = 3  # Default neutral rating
                
        # Ensure comments are not empty and meaningful
        if not comments or len(comments.strip()) < 3:
            comments = message_body.strip()
        
        return rating, comments
    
    def _send_feedback_confirmation(self, mobile_number, rating, feedback):
        """Send immediate confirmation that feedback was received"""
        try:
            whatsapp_service = self.env['cater.whatsapp.service'].search([('active', '=', True)], limit=1)
            if not whatsapp_service:
                return
            
            # Create personalized confirmation based on rating
            confirmation_message = f"""✅ *Feedback Received - Thank You!*

🙏 Thank you for your {rating}-star rating for *{self.event_name}*!

*Your feedback:*
{"⭐" * rating} ({rating}/5 stars)
💬 "{feedback.comments}"

"""
            
            if rating >= 4:
                confirmation_message += f"""🌟 *We're delighted you loved our service!*

Your positive feedback makes our team's day! Here's how you can help us grow:

🔗 *Leave a Google Review:* 
   Help others discover our catering services
   
� *Refer Friends & Family:* 
   Share our contact: +233-XXX-XXXX
   
🎉 *Special Thank You Offer:*
   Get 10% OFF your next booking!
   Code: HAPPY{rating}STAR
   Valid until: {(fields.Date.today() + timedelta(days=30)).strftime('%B %d, %Y')}

📱 *Follow us on social media:*
   📘 Facebook: [Your Facebook Page]
   📸 Instagram: @yourcatering

We can't wait to cater your next celebration! 💚"""
            else:
                confirmation_message += f"""📞 *We want to make this right.*

Your feedback is incredibly valuable to us. We take every comment seriously.

*Immediate Action:*
✅ Your concerns have been escalated to our management team
✅ A senior manager will contact you within 4 hours
✅ We're committed to resolving any issues

*How we'll follow up:*
• Personal call to understand your experience
• Review what went wrong and how to improve  
• Offer appropriate compensation for any inconvenience
• Ensure your next experience exceeds expectations

*Contact us directly if urgent:*
📞 Manager Hotline: +233-XXX-XXXX
📧 Email: manager@yourcatering.com
💬 WhatsApp: This number

Your trust means everything to us. Thank you for giving us the opportunity to improve. 🙏

*Ref #FB{feedback.id:04d}*"""
            
            whatsapp_service.send_message(mobile_number, confirmation_message)
            _logger.info(f"Enhanced feedback confirmation sent for booking {self.name} with {rating} stars")
            
        except Exception as e:
            _logger.error(f"Failed to send feedback confirmation: {str(e)}")

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

    booking_id = fields.Many2one('cater.event.booking', 'Booking', required=True, ondelete='cascade')
    menu_item_id = fields.Many2one('cater.menu.item', 'Menu Item', required=True)
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

    booking_id = fields.Many2one('cater.event.booking', 'Booking', required=True, ondelete='cascade')
    service_id = fields.Many2one('cater.service', 'Service', required=True)
    quantity = fields.Integer('Quantity', required=True, default=1)
    price_unit = fields.Monetary('Unit Price', related='service_id.price', store=True)
    currency_id = fields.Many2one('res.currency', related='booking_id.currency_id')
    subtotal = fields.Monetary('Subtotal', compute='_compute_subtotal', store=True)
    notes = fields.Char('Special Notes')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
