# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CrmLeadExtend(models.Model):
    """
    Extend CRM Lead for catering integration
    Adds booking conversion functionality and bidirectional relationship
    """
    _inherit = 'crm.lead'

    # Link to customer request
    customer_request_id = fields.Many2one(
        'cater.customer.request',
        string='Customer Request',
        readonly=True,
        help='Original customer request that created this lead'
    )
    
    # Link to booking
    booking_id = fields.Many2one(
        'cater.event.booking',
        string='Event Booking',
        readonly=True,
        copy=False,
        help='Event booking created from this lead'
    )
    
    booking_count = fields.Integer(
        string='Booking Count',
        compute='_compute_booking_count'
    )
    
    # Additional catering-specific fields
    event_date = fields.Date(
        string='Event Date',
        help='Requested event date'
    )
    
    guest_count = fields.Integer(
        string='Expected Guests',
        help='Number of expected guests'
    )
    
    venue_location = fields.Char(
        string='Venue/Location',
        help='Event venue or location'
    )
    
    # Package and menu items
    interested_package_id = fields.Many2one(
        'cater.package',
        string='Interested Package',
        help='Package the customer is interested in'
    )
    
    interested_menu_item_ids = fields.Many2many(
        'cater.menu.item',
        'crm_lead_menu_item_rel',
        'lead_id',
        'menu_item_id',
        string='Interested Menu Items',
        help='Menu items the customer is interested in'
    )

    @api.depends('booking_id')
    def _compute_booking_count(self):
        """Compute number of related bookings"""
        for lead in self:
            lead.booking_count = 1 if lead.booking_id else 0

    def action_convert_to_booking(self):
        """
        Convert CRM lead to event booking
        Transfers scheduling, notes, and expected revenue to the booking
        """
        self.ensure_one()
        
        if self.booking_id:
            raise UserError(_('This lead has already been converted to a booking.'))
        
        if not self.partner_id:
            raise UserError(_('Please select a customer before converting to booking.'))
        
        # Ensure lead is in won stage
        if not self.stage_id.is_won:
            # Ask user to mark as won first
            return {
                'type': 'ir.actions.act_window',
                'name': _('Mark Lead as Won'),
                'res_model': 'crm.lead',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_stage_id': self.env.ref('cater.stage_lead_won', raise_if_not_found=False).id
                }
            }
        
        # Extract event information from lead description or fields
        event_name = self.name or 'Event from Lead'
        event_date = self.event_date or self.date_deadline or fields.Date.today()
        # Use the lead's guest_count if set, otherwise default to 1
        guest_count = self.guest_count if self.guest_count else 1
        venue = self.venue_location if self.venue_location else ''
        
        _logger.info(f"Converting lead {self.id} to booking - guest_count: {self.guest_count}, venue_location: {self.venue_location}")
        _logger.info(f"Booking values - guest_count: {guest_count}, venue: {venue}")
        
        # Determine event type from lead tags or default to 'other'
        event_type = 'other'
        wedding_tag = self.env.ref('cater.tag_wedding', raise_if_not_found=False)
        corporate_tag = self.env.ref('cater.tag_corporate_event', raise_if_not_found=False)
        
        if wedding_tag and wedding_tag in self.tag_ids:
            event_type = 'wedding'
        elif corporate_tag and corporate_tag in self.tag_ids:
            event_type = 'corporate'
        
        # Prepare booking description from lead notes
        booking_description = ''
        if self.description:
            booking_description += f"From CRM Lead:\n{self.description}"
        
        # Calculate deposit (20% of expected revenue)
        deposit_amount = self.expected_revenue * 0.2 if self.expected_revenue else 0.0
        
        # Create booking
        booking_vals = {
            'partner_id': self.partner_id.id,
            'event_name': event_name,
            'event_type': event_type,
            'event_date': event_date,
            'guest_count': guest_count,
            'venue': venue,
            'state': 'draft',
            'special_requests': booking_description,
            'lead_id': self.id,
            'company_id': self.company_id.id,
        }
        
        # Add package if customer selected one
        if self.interested_package_id:
            booking_vals['package_id'] = self.interested_package_id.id
        
        # Set deposit if we have expected revenue
        if deposit_amount > 0:
            booking_vals['deposit_amount'] = deposit_amount
        
        booking = self.env['cater.event.booking'].create(booking_vals)
        
        # Add menu items if customer selected any (and no package selected)
        # If package is selected, the onchange will handle menu items
        if self.interested_menu_item_ids and not self.interested_package_id:
            menu_line_vals = []
            for menu_item in self.interested_menu_item_ids:
                menu_line_vals.append((0, 0, {
                    'menu_item_id': menu_item.id,
                    'quantity': self.guest_count if self.guest_count else 1,
                    'notes': 'From customer interest'
                }))
            booking.write({'menu_line_ids': menu_line_vals})
        
        # Update lead
        self.write({
            'booking_id': booking.id,
        })
        
        # Copy activities to booking
        for activity in self.activity_ids:
            self.env['mail.activity'].create({
                'res_id': booking.id,
                'res_model_id': self.env['ir.model']._get('cater.event.booking').id,
                'activity_type_id': activity.activity_type_id.id,
                'summary': activity.summary,
                'note': activity.note,
                'date_deadline': activity.date_deadline,
                'user_id': activity.user_id.id,
            })
        
        # Post message on lead
        self.message_post(
            body=_('Converted to Event Booking: <a href="#" data-oe-model="cater.event.booking" data-oe-id="%s">%s</a>') % (booking.id, booking.name)
        )
        
        # Post message on booking
        booking.message_post(
            body=_('Created from CRM Lead: <a href="#" data-oe-model="crm.lead" data-oe-id="%s">%s</a><br/>Expected Revenue: ₵%.2f') % (self.id, self.name, self.expected_revenue or 0.0)
        )
        
        _logger.info(f"Lead {self.name} converted to booking {booking.name} with expected revenue: {self.expected_revenue}")
        
        # Return action to view the booking
        return {
            'type': 'ir.actions.act_window',
            'name': _('Event Booking'),
            'res_model': 'cater.event.booking',
            'res_id': booking.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_booking(self):
        """View related booking"""
        self.ensure_one()
        if not self.booking_id:
            raise UserError(_('No booking has been created from this lead yet.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Event Booking'),
            'res_model': 'cater.event.booking',
            'res_id': self.booking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_customer_request(self):
        """View originating customer request"""
        self.ensure_one()
        if not self.customer_request_id:
            raise UserError(_('This lead was not created from a customer request.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Request'),
            'res_model': 'cater.customer.request',
            'res_id': self.customer_request_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
