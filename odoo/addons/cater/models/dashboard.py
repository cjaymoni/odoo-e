from odoo import models, fields, api, tools
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class CateringDashboard(models.Model):
    _name = 'cater.dashboard'
    _description = 'Catering Dashboard Data'

    @api.model
    @tools.ormcache('self.env.uid')
    def get_dashboard_data(self):
        """Get comprehensive dashboard data with caching"""
        try:
            return {
                'kpis': self._get_kpi_data(),
                'charts': self._get_chart_data(),
                'recent_activity': self._get_recent_activity(),
                'feedback_summary': self._get_feedback_summary(),
                'upcoming_events': self._get_upcoming_events(),
                'financial_summary': self._get_financial_summary()
            }
        except Exception as e:
            _logger.error(f"Error getting dashboard data: {str(e)}")
            return self._get_empty_dashboard_data()
    
    def _get_empty_dashboard_data(self):
        """Return empty dashboard data structure"""
        return {
            'kpis': {
                'total_bookings': 0,
                'booking_growth': 0,
                'total_revenue': 0,
                'revenue_growth': 0,
                'avg_satisfaction': 0,
                'completed_events': 0,
                'active_customers': 0,
                'pending_bookings': 0
            },
            'charts': {
                'booking_trends': [],
                'revenue_trends': [],
                'event_type_distribution': [],
                'rating_distribution': [],
                'monthly_performance': []
            },
            'recent_activity': [],
            'feedback_summary': {
                'total_feedback': 0,
                'avg_rating': 0,
                'recommendation_rate': 0,
                'response_rate': 0,
                'detailed_ratings': {
                    'food_quality': 0,
                    'service_quality': 0,
                    'presentation': 0,
                    'timeliness': 0,
                }
            },
            'upcoming_events': [],
            'financial_summary': {
                'monthly': {'revenue': 0, 'paid': 0, 'pending': 0},
                'yearly': {'revenue': 0, 'paid': 0, 'pending': 0}
            }
        }
    
    @api.model
    def clear_dashboard_cache(self):
        """Clear dashboard cache when data changes"""
        self.env.invalidate_all()
        # Clear ormcache for the get_dashboard_data method
        # Since it's cached by self.env.uid, we clear for current user
        try:
            self.get_dashboard_data.clear_cache(self, self.env.uid)
        except (AttributeError, TypeError):
            # Fallback: invalidate all if clear_cache fails
            self.env.invalidate_all()
    
    def _get_kpi_data(self):
        """Get Key Performance Indicators"""
        today = fields.Date.today()
        month_start = today.replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        
        # This month's data
        this_month_bookings = self.env['cater.event.booking'].search([
            ('create_date', '>=', month_start),
            ('state', 'in', ['confirmed', 'completed'])
        ])
        
        # Last month's data for comparison
        last_month_bookings = self.env['cater.event.booking'].search([
            ('create_date', '>=', last_month_start),
            ('create_date', '<', month_start),
            ('state', 'in', ['confirmed', 'completed'])
        ])
        
        # Revenue calculations
        this_month_revenue = sum(this_month_bookings.mapped('total_amount'))
        last_month_revenue = sum(last_month_bookings.mapped('total_amount'))
        
        # Growth calculations
        booking_growth = self._calculate_growth(len(this_month_bookings), len(last_month_bookings))
        revenue_growth = self._calculate_growth(this_month_revenue, last_month_revenue)
        
        # Average satisfaction
        feedback_this_month = self.env['cater.feedback'].search([
            ('create_date', '>=', month_start)
        ])
        avg_rating = 0
        if feedback_this_month:
            ratings = [int(f.rating) for f in feedback_this_month if f.rating]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            'total_bookings': len(this_month_bookings),
            'booking_growth': booking_growth,
            'total_revenue': this_month_revenue,
            'revenue_growth': revenue_growth,
            'avg_satisfaction': round(avg_rating, 1),
            'completed_events': len(this_month_bookings.filtered(lambda b: b.state == 'completed')),
            'active_customers': len(this_month_bookings.mapped('partner_id')),
            'pending_bookings': len(self.env['cater.event.booking'].search([('state', '=', 'draft')]))
        }
    
    def _get_chart_data(self):
        """Get data for dashboard charts"""
        return {
            'booking_trends': self._get_booking_trends(),
            'revenue_trends': self._get_revenue_trends(),
            'event_type_distribution': self._get_event_type_distribution(),
            'rating_distribution': self._get_rating_distribution(),
            'monthly_performance': self._get_monthly_performance()
        }
    
    def _get_booking_trends(self):
        """Get booking trends for the last 6 months"""
        data = []
        for i in range(6):
            date = fields.Date.today() - timedelta(days=30*i)
            month_start = date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            bookings = self.env['cater.event.booking'].search([
                ('create_date', '>=', month_start),
                ('create_date', '<=', month_end),
                ('state', 'in', ['confirmed', 'completed'])
            ])
            
            data.append({
                'month': month_start.strftime('%B %Y'),
                'bookings': len(bookings),
                'revenue': sum(bookings.mapped('total_amount'))
            })
        
        return list(reversed(data))
    
    def _get_revenue_trends(self):
        """Get revenue trends by month"""
        trends = self._get_booking_trends()
        return [{
            'month': item['month'],
            'revenue': item['revenue']
        } for item in trends]
    
    def _get_event_type_distribution(self):
        """Get distribution of event types"""
        bookings = self.env['cater.event.booking'].search([
            ('state', 'in', ['confirmed', 'completed']),
            ('create_date', '>=', fields.Date.today() - timedelta(days=365))
        ])
        
        event_types = {}
        for booking in bookings:
            event_type = dict(booking._fields['event_type'].selection).get(booking.event_type, booking.event_type)
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return [{'type': k, 'count': v} for k, v in event_types.items()]
    
    def _get_rating_distribution(self):
        """Get distribution of customer ratings"""
        feedback = self.env['cater.feedback'].search([
            ('create_date', '>=', fields.Date.today() - timedelta(days=365))
        ])
        
        ratings = {}
        for f in feedback:
            if f.rating:
                star_label = f"{f.rating} Star{'s' if f.rating != '1' else ''}"
                ratings[star_label] = ratings.get(star_label, 0) + 1
        
        return [{'rating': k, 'count': v} for k, v in ratings.items()]
    
    def _get_monthly_performance(self):
        """Get monthly performance metrics"""
        data = []
        for i in range(12):
            date = fields.Date.today() - timedelta(days=30*i)
            month_start = date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            bookings = self.env['cater.event.booking'].search([
                ('event_date', '>=', month_start),
                ('event_date', '<=', month_end),
                ('state', 'in', ['confirmed', 'completed'])
            ])
            
            feedback = self.env['cater.feedback'].search([
                ('booking_id', 'in', bookings.ids)
            ])
            
            avg_rating = 0
            if feedback:
                ratings = [int(f.rating) for f in feedback if f.rating]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            data.append({
                'month': month_start.strftime('%b %Y'),
                'bookings': len(bookings),
                'revenue': sum(bookings.mapped('total_amount')),
                'satisfaction': round(avg_rating, 1)
            })
        
        return list(reversed(data))
    
    def _get_recent_activity(self):
        """Get recent booking and feedback activity"""
        recent_bookings = self.env['cater.event.booking'].search([
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=7))
        ], order='create_date desc', limit=5)
        
        recent_feedback = self.env['cater.feedback'].search([
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=7))
        ], order='create_date desc', limit=5)
        
        activity = []
        
        for booking in recent_bookings:
            activity.append({
                'type': 'booking',
                'title': f"New booking: {booking.event_name}",
                'description': f"{booking.partner_id.name} - {booking.event_type}",
                'date': booking.create_date,
                'icon': 'calendar'
            })
        
        for feedback in recent_feedback:
            activity.append({
                'type': 'feedback',
                'title': f"New feedback: {feedback.rating} stars",
                'description': f"{feedback.partner_id.name} - {feedback.booking_id.event_name}",
                'date': feedback.create_date,
                'icon': 'star'
            })
        
        # Sort by date
        activity.sort(key=lambda x: x['date'], reverse=True)
        return activity[:10]
    
    def _get_feedback_summary(self):
        """Get feedback summary statistics"""
        feedback = self.env['cater.feedback'].search([
            ('create_date', '>=', fields.Date.today() - timedelta(days=30))
        ])
        
        if not feedback:
            return {
                'total_feedback': 0,
                'avg_rating': 0,
                'recommendation_rate': 0,
                'response_rate': 0
            }
        
        ratings = [int(f.rating) for f in feedback if f.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        recommendations = len(feedback.filtered('would_recommend'))
        recommendation_rate = (recommendations / len(feedback)) * 100 if feedback else 0
        
        # Calculate response rate (feedback vs completed bookings)
        completed_bookings = self.env['cater.event.booking'].search([
            ('state', '=', 'completed'),
            ('event_date', '>=', fields.Date.today() - timedelta(days=30))
        ])
        response_rate = (len(feedback) / len(completed_bookings)) * 100 if completed_bookings else 0
        
        return {
            'total_feedback': len(feedback),
            'avg_rating': round(avg_rating, 1),
            'recommendation_rate': round(recommendation_rate, 1),
            'response_rate': round(response_rate, 1),
            'detailed_ratings': {
                'food_quality': round(sum(feedback.mapped('food_quality')) / len(feedback), 1) if feedback else 0,
                'service_quality': round(sum(feedback.mapped('service_quality')) / len(feedback), 1) if feedback else 0,
                'presentation': round(sum(feedback.mapped('presentation')) / len(feedback), 1) if feedback else 0,
                'timeliness': round(sum(feedback.mapped('timeliness')) / len(feedback), 1) if feedback else 0,
            }
        }
    
    def _get_upcoming_events(self):
        """Get upcoming events for the next 7 days"""
        start_date = fields.Date.today()
        end_date = start_date + timedelta(days=7)
        
        upcoming = self.env['cater.event.booking'].search([
            ('event_date', '>=', start_date),
            ('event_date', '<=', end_date),
            ('state', 'in', ['confirmed', 'in_progress'])
        ], order='event_date asc')
        
        events = []
        for booking in upcoming:
            events.append({
                'id': booking.id,
                'name': booking.event_name,
                'customer': booking.partner_id.name,
                'date': booking.event_date,
                'venue': booking.venue,
                'guests': booking.guest_count,
                'status': booking.state,
                'total': booking.total_amount
            })
        
        return events
    
    def _get_financial_summary(self):
        """Get financial summary for current period"""
        today = fields.Date.today()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        # Monthly financials
        monthly_bookings = self.env['cater.event.booking'].search([
            ('create_date', '>=', month_start),
            ('state', 'in', ['confirmed', 'completed'])
        ])
        
        # Yearly financials
        yearly_bookings = self.env['cater.event.booking'].search([
            ('create_date', '>=', year_start),
            ('state', 'in', ['confirmed', 'completed'])
        ])
        
        return {
            'monthly': {
                'revenue': sum(monthly_bookings.mapped('total_amount')),
                'paid': sum(monthly_bookings.mapped('paid_amount')),
                'pending': sum(monthly_bookings.mapped('balance_due'))
            },
            'yearly': {
                'revenue': sum(yearly_bookings.mapped('total_amount')),
                'paid': sum(yearly_bookings.mapped('paid_amount')),
                'pending': sum(yearly_bookings.mapped('balance_due'))
            }
        }
    
    def _calculate_growth(self, current, previous):
        """Calculate growth percentage"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)
