from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta
import base64
import io
import xlsxwriter


class CateringReport(models.TransientModel):
    _name = 'cater.report.wizard'
    _description = 'Catering Report Wizard'

    report_type = fields.Selection([
        ('feedback_summary', 'Customer Feedback Summary'),
        ('satisfaction_trends', 'Customer Satisfaction Trends'),
        ('booking_analysis', 'Booking Analysis'),
        ('financial_summary', 'Financial Summary'),
        ('performance_metrics', 'Performance Metrics')
    ], string='Report Type', required=True, default='feedback_summary')
    
    date_from = fields.Date('From Date', required=True, 
                           default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date('To Date', required=True, 
                         default=fields.Date.today)
    
    partner_ids = fields.Many2many('res.partner', string='Customers',
                                  domain=[('is_catering_customer', '=', True)])
    event_type = fields.Selection([
        ('wedding', 'Wedding'),
        ('birthday', 'Birthday Party'),
        ('corporate', 'Corporate Event'),
        ('funeral', 'Funeral'),
        ('outdooring', 'Outdooring'),
        ('graduation', 'Graduation'),
        ('other', 'Other')
    ], string='Event Type')
    
    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV')
    ], string='Export Format', default='pdf')

    def action_generate_report(self):
        """Generate the selected report"""
        if self.report_type == 'feedback_summary':
            return self._generate_feedback_summary()
        elif self.report_type == 'satisfaction_trends':
            return self._generate_satisfaction_trends()
        elif self.report_type == 'booking_analysis':
            return self._generate_booking_analysis()
        elif self.report_type == 'financial_summary':
            return self._generate_financial_summary()
        elif self.report_type == 'performance_metrics':
            return self._generate_performance_metrics()

    def _get_base_domain(self):
        """Get base domain for filtering"""
        domain = [
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ]
        
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
            
        return domain

    def _generate_feedback_summary(self):
        """Generate feedback summary report"""
        domain = self._get_base_domain()
        
        # Get feedback data
        feedback_data = self.env['cater.feedback'].search(domain)
        
        # Get related bookings for additional context
        booking_domain = self._get_base_domain()
        if self.event_type:
            booking_domain.append(('event_type', '=', self.event_type))
        
        bookings = self.env['cater.event.booking'].search(booking_domain)
        
        # Calculate statistics
        total_feedback = len(feedback_data)
        total_bookings = len(bookings.filtered(lambda b: b.state == 'completed'))
        response_rate = (total_feedback / total_bookings * 100) if total_bookings > 0 else 0
        
        # Rating analysis
        ratings = feedback_data.mapped('rating')
        avg_rating = sum([int(r) for r in ratings if r]) / len(ratings) if ratings else 0
        
        rating_distribution = {}
        for rating in ['1', '2', '3', '4', '5']:
            count = len(feedback_data.filtered(lambda f: f.rating == rating))
            rating_distribution[rating] = count
        
        # Detailed ratings
        detailed_ratings = {
            'food_quality': sum(feedback_data.mapped('food_quality')) / total_feedback if total_feedback else 0,
            'service_quality': sum(feedback_data.mapped('service_quality')) / total_feedback if total_feedback else 0,
            'presentation': sum(feedback_data.mapped('presentation')) / total_feedback if total_feedback else 0,
            'timeliness': sum(feedback_data.mapped('timeliness')) / total_feedback if total_feedback else 0,
        }
        
        # Recommendation rate
        recommendations = len(feedback_data.filtered('would_recommend'))
        recommendation_rate = (recommendations / total_feedback * 100) if total_feedback > 0 else 0
        
        data = {
            'report_title': 'Customer Feedback Summary Report',
            'date_range': f"{self.date_from} to {self.date_to}",
            'total_feedback': total_feedback,
            'total_bookings': total_bookings,
            'response_rate': round(response_rate, 1),
            'avg_rating': round(avg_rating, 2),
            'rating_distribution': rating_distribution,
            'detailed_ratings': detailed_ratings,
            'recommendation_rate': round(recommendation_rate, 1),
            'feedback_details': feedback_data,
            'bookings': bookings
        }
        
        if self.export_format == 'xlsx':
            return self._export_to_excel(data, 'feedback_summary')
        elif self.export_format == 'csv':
            return self._export_to_csv(data, 'feedback_summary')
        else:
            return self._export_to_pdf(data, 'feedback_summary')

    def _generate_satisfaction_trends(self):
        """Generate satisfaction trends report"""
        domain = self._get_base_domain()
        feedback_data = self.env['cater.feedback'].search(domain)
        
        # Group by month
        monthly_data = {}
        for feedback in feedback_data:
            month_key = feedback.create_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(int(feedback.rating) if feedback.rating else 0)
        
        # Calculate monthly averages
        trends = []
        for month, ratings in monthly_data.items():
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            trends.append({
                'month': datetime.strptime(month, '%Y-%m').strftime('%B %Y'),
                'avg_rating': round(avg_rating, 2),
                'total_feedback': len(ratings)
            })
        
        trends.sort(key=lambda x: x['month'])
        
        data = {
            'report_title': 'Customer Satisfaction Trends',
            'date_range': f"{self.date_from} to {self.date_to}",
            'trends': trends,
            'total_periods': len(trends)
        }
        
        if self.export_format == 'xlsx':
            return self._export_to_excel(data, 'satisfaction_trends')
        else:
            return self._export_to_pdf(data, 'satisfaction_trends')

    def _generate_booking_analysis(self):
        """Generate booking analysis report"""
        booking_domain = self._get_base_domain()
        if self.event_type:
            booking_domain.append(('event_type', '=', self.event_type))
        
        bookings = self.env['cater.event.booking'].search(booking_domain)
        
        # Analysis by event type
        event_type_analysis = {}
        for booking in bookings:
            event_type = booking.event_type
            if event_type not in event_type_analysis:
                event_type_analysis[event_type] = {
                    'count': 0,
                    'total_revenue': 0,
                    'avg_guests': 0,
                    'guests_total': 0
                }
            
            event_type_analysis[event_type]['count'] += 1
            event_type_analysis[event_type]['total_revenue'] += booking.total_amount
            event_type_analysis[event_type]['guests_total'] += booking.guest_count
        
        # Calculate averages
        for event_type, data in event_type_analysis.items():
            if data['count'] > 0:
                data['avg_revenue'] = data['total_revenue'] / data['count']
                data['avg_guests'] = data['guests_total'] / data['count']
        
        # Status analysis
        status_analysis = {}
        for status in ['draft', 'confirmed', 'in_progress', 'completed', 'cancelled']:
            count = len(bookings.filtered(lambda b: b.state == status))
            status_analysis[status] = count
        
        data = {
            'report_title': 'Booking Analysis Report',
            'date_range': f"{self.date_from} to {self.date_to}",
            'total_bookings': len(bookings),
            'total_revenue': sum(bookings.mapped('total_amount')),
            'event_type_analysis': event_type_analysis,
            'status_analysis': status_analysis,
            'bookings': bookings
        }
        
        if self.export_format == 'xlsx':
            return self._export_to_excel(data, 'booking_analysis')
        else:
            return self._export_to_pdf(data, 'booking_analysis')

    def _export_to_excel(self, data, report_type):
        """Export report to Excel format"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Create worksheet
        worksheet = workbook.add_worksheet(data['report_title'])
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        cell_format = workbook.add_format({'border': 1})
        
        # Write title
        worksheet.merge_range('A1:F1', data['report_title'], title_format)
        worksheet.write('A2', f"Date Range: {data['date_range']}")
        
        row = 4
        
        if report_type == 'feedback_summary':
            # Summary statistics
            worksheet.write(row, 0, 'Total Feedback:', header_format)
            worksheet.write(row, 1, data['total_feedback'], cell_format)
            row += 1
            
            worksheet.write(row, 0, 'Response Rate:', header_format)
            worksheet.write(row, 1, f"{data['response_rate']}%", cell_format)
            row += 1
            
            worksheet.write(row, 0, 'Average Rating:', header_format)
            worksheet.write(row, 1, data['avg_rating'], cell_format)
            row += 2
            
            # Rating distribution
            worksheet.write(row, 0, 'Rating Distribution:', header_format)
            row += 1
            for rating, count in data['rating_distribution'].items():
                worksheet.write(row, 0, f"{rating} Stars:", cell_format)
                worksheet.write(row, 1, count, cell_format)
                row += 1
        
        workbook.close()
        output.seek(0)
        
        attachment = self.env['ir.attachment'].create({
            'name': f"{data['report_title']}.xlsx",
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'store_fname': f"{report_type}_{fields.Date.today()}.xlsx",
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self'
        }

    def _export_to_csv(self, data, report_type):
        """Export report to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([data['report_title']])
        writer.writerow([f"Date Range: {data['date_range']}"])
        writer.writerow([])
        
        if report_type == 'feedback_summary':
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Feedback', data['total_feedback']])
            writer.writerow(['Response Rate', f"{data['response_rate']}%"])
            writer.writerow(['Average Rating', data['avg_rating']])
            writer.writerow([])
            
            writer.writerow(['Rating', 'Count'])
            for rating, count in data['rating_distribution'].items():
                writer.writerow([f"{rating} Stars", count])
        
        csv_data = output.getvalue().encode('utf-8')
        
        attachment = self.env['ir.attachment'].create({
            'name': f"{data['report_title']}.csv",
            'type': 'binary',
            'datas': base64.b64encode(csv_data),
            'store_fname': f"{report_type}_{fields.Date.today()}.csv",
            'mimetype': 'text/csv'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self'
        }

    def _export_to_pdf(self, data, report_type):
        """Export report to PDF format"""
        return self.env.ref(f'cater.action_report_{report_type}').report_action(self, data=data)
