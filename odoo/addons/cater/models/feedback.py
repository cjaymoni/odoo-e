from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class CateringFeedback(models.Model):
    _name = 'cater.feedback'
    _description = 'Customer Feedback'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _sql_constraints = [
        ('unique_booking_feedback', 'UNIQUE(booking_id)', 
         'Only one feedback per booking is allowed!'),
        ('valid_rating_range', 'CHECK(rating::int >= 1 AND rating::int <= 5)', 
         'Rating must be between 1 and 5!'),
    ]

    def init(self):
        """Create database indexes for performance"""
        super().init()
        # Create indexes using SQL
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_feedback_rating 
            ON cater_feedback(rating);
        """)
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_cater_feedback_create_date 
            ON cater_feedback(create_date);
        """)

    booking_id = fields.Many2one('cater.event.booking', 'Booking', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', related='booking_id.partner_id', store=True)
    rating = fields.Selection([
        ('1', '1 Star - Poor'),
        ('2', '2 Stars - Fair'),
        ('3', '3 Stars - Good'),
        ('4', '4 Stars - Very Good'),
        ('5', '5 Stars - Excellent')
    ], 'Rating', required=True, tracking=True)
    
    # Detailed ratings with validation
    food_quality = fields.Integer('Food Quality (1-5)', default=5)
    service_quality = fields.Integer('Service Quality (1-5)', default=5)
    presentation = fields.Integer('Presentation (1-5)', default=5)
    timeliness = fields.Integer('Timeliness (1-5)', default=5)
    
    comments = fields.Text('Comments')
    would_recommend = fields.Boolean('Would Recommend', default=True)
    feedback_date = fields.Datetime('Feedback Date', default=fields.Datetime.now)
    source = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Phone Call'),
        ('email', 'Email'),
        ('in_person', 'In Person')
    ], 'Feedback Source', default='whatsapp')
    
    # Computed fields for analytics
    overall_score = fields.Float('Overall Score', compute='_compute_overall_score', store=True)
    is_positive = fields.Boolean('Positive Feedback', compute='_compute_is_positive', store=True)
    
    @api.depends('food_quality', 'service_quality', 'presentation', 'timeliness')
    def _compute_overall_score(self):
        """Compute overall score from detailed ratings"""
        for record in self:
            if all([record.food_quality, record.service_quality, 
                   record.presentation, record.timeliness]):
                record.overall_score = (
                    record.food_quality + record.service_quality + 
                    record.presentation + record.timeliness
                ) / 4.0
            else:
                record.overall_score = 0.0
    
    @api.depends('rating')
    def _compute_is_positive(self):
        """Determine if feedback is positive (4+ stars)"""
        for record in self:
            record.is_positive = int(record.rating) >= 4 if record.rating else False
    
    @api.constrains('food_quality', 'service_quality', 'presentation', 'timeliness')
    def _check_detailed_ratings(self):
        """Validate detailed rating ranges"""
        for record in self:
            ratings = [record.food_quality, record.service_quality, 
                      record.presentation, record.timeliness]
            for rating in ratings:
                if rating < 1 or rating > 5:
                    raise ValidationError(_("Detailed ratings must be between 1 and 5."))
    
    @api.constrains('booking_id')
    def _check_booking_completed(self):
        """Ensure feedback is only for completed bookings"""
        for record in self:
            if record.booking_id.state != 'completed':
                raise ValidationError(_("Feedback can only be provided for completed bookings."))
    
    @api.constrains('feedback_date', 'booking_id')
    def _check_feedback_timing(self):
        """Ensure feedback is provided after the event"""
        for record in self:
            if record.feedback_date < record.booking_id.event_date:
                raise ValidationError(_("Feedback cannot be provided before the event date."))
    
    @api.model
    def create_from_whatsapp(self, booking_id, rating, comments):
        """Create feedback from WhatsApp response with validation"""
        booking = self.env['cater.event.booking'].browse(booking_id)
        
        # Check if feedback already exists
        existing_feedback = self.search([('booking_id', '=', booking_id)])
        if existing_feedback:
            raise ValidationError(_("Feedback for this booking already exists."))
        
        # Validate booking state
        if booking.state != 'completed':
            raise ValidationError(_("Cannot create feedback for non-completed booking."))
        
        feedback = self.create({
            'booking_id': booking_id,
            'rating': str(rating),
            'comments': comments,
            'source': 'whatsapp',
            'food_quality': rating,
            'service_quality': rating,
            'presentation': rating,
            'timeliness': rating,
        })
        
        # Trigger confirmation and follow-up processes
        booking._send_feedback_confirmation(booking.partner_id.mobile, rating, feedback)
        
        if rating < 4:
            booking._create_followup_activity(feedback)
        
        return feedback
    
    def action_mark_helpful(self):
        """Mark feedback as helpful (for staff use)"""
        self.ensure_one()
        self.message_post(
            body=_("This feedback has been marked as helpful by staff."),
            message_type='notification'
        )
    
    def action_follow_up(self):
        """Create follow-up activity for negative feedback"""
        self.ensure_one()
        if not self.is_positive:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_call').id,
                'note': f"Follow up on negative feedback for booking {self.booking_id.name}",
                'res_id': self.booking_id.id,
                'res_model_id': self.env.ref('cater.model_cater_event_booking').id,
                'user_id': self.env.user.id,
                'date_deadline': fields.Date.today() + timedelta(days=1)
            })
    
    @api.model
    def get_satisfaction_metrics(self, date_from=None, date_to=None):
        """Get satisfaction metrics for dashboard"""
        domain = []
        if date_from:
            domain.append(('create_date', '>=', date_from))
        if date_to:
            domain.append(('create_date', '<=', date_to))
        
        feedback_records = self.search(domain)
        
        if not feedback_records:
            return {
                'avg_rating': 0,
                'total_feedback': 0,
                'positive_rate': 0,
                'recommendation_rate': 0
            }
        
        ratings = [int(f.rating) for f in feedback_records if f.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        positive_count = len(feedback_records.filtered('is_positive'))
        positive_rate = (positive_count / len(feedback_records)) * 100
        
        recommendations = len(feedback_records.filtered('would_recommend'))
        recommendation_rate = (recommendations / len(feedback_records)) * 100
        
        return {
            'avg_rating': round(avg_rating, 2),
            'total_feedback': len(feedback_records),
            'positive_rate': round(positive_rate, 1),
            'recommendation_rate': round(recommendation_rate, 1)
        }

    @api.model
    def get_recent_feedback_activity(self, limit=10):
        """Get recent feedback activity for real-time dashboard"""
        recent_feedback = self.search([], order='create_date desc', limit=limit)
        
        activity_data = []
        for feedback in recent_feedback:
            activity_data.append({
                'id': feedback.id,
                'customer_name': feedback.partner_id.name,
                'event_name': feedback.booking_id.event_name,
                'rating': int(feedback.rating),
                'rating_stars': "⭐" * int(feedback.rating),
                'comments': feedback.comments[:100] + "..." if len(feedback.comments or "") > 100 else feedback.comments,
                'source': feedback.source,
                'feedback_date': feedback.feedback_date,
                'is_positive': feedback.is_positive,
                'booking_reference': feedback.booking_id.name,
                'time_ago': self._get_time_ago(feedback.feedback_date),
            })
        
        return activity_data
    
    def _get_time_ago(self, date):
        """Get human-readable time ago string"""
        from datetime import datetime
        
        if not date:
            return "Unknown"
            
        now = fields.Datetime.now()
        diff = now - date
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
