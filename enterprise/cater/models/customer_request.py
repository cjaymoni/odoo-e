# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CustomerRequest(models.Model):
    """
    Customer Request Model - Initial inquiry/request before lead conversion
    Captures early stage inquiries that can be converted to CRM leads
    """
    _name = 'cater.customer.request'
    _description = 'Customer Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Request Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True
    )
    
    partner_email = fields.Char(
        related='partner_id.email',
        string='Email',
        store=True
    )
    
    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Phone',
        store=True
    )
    
    event_type = fields.Selection([
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate Event'),
        ('birthday', 'Birthday Party'),
        ('anniversary', 'Anniversary'),
        ('conference', 'Conference'),
        ('meeting', 'Meeting/Seminar'),
        ('other', 'Other')
    ], string='Event Type', required=True, tracking=True)
    
    event_date = fields.Date(
        string='Requested Event Date',
        tracking=True
    )
    
    guest_count = fields.Integer(
        string='Expected Guests',
        tracking=True
    )
    
    service_type = fields.Selection([
        ('catering_only', 'Catering Only'),
        ('full_service', 'Full Service (Catering + Decoration)'),
        ('equipment_rental', 'Equipment Rental'),
        ('staff_only', 'Staff Only'),
        ('custom', 'Custom Package')
    ], string='Service Type', tracking=True)
    
    venue_location = fields.Char(
        string='Venue/Location',
        tracking=True
    )
    
    budget_range = fields.Selection([
        ('under_1000', 'Under ₵1,000'),
        ('1000_3000', '₵1,000 - ₵3,000'),
        ('3000_5000', '₵3,000 - ₵5,000'),
        ('5000_10000', '₵5,000 - ₵10,000'),
        ('above_10000', 'Above ₵10,000')
    ], string='Budget Range', tracking=True)
    
    # Package and Menu Items
    package_id = fields.Many2one(
        'cater.package',
        string='Interested Package',
        tracking=True,
        help="Package the customer is interested in"
    )
    
    menu_item_ids = fields.Many2many(
        'cater.menu.item',
        'customer_request_menu_item_rel',
        'request_id',
        'menu_item_id',
        string='Interested Menu Items',
        help="Menu items the customer is interested in"
    )
    
    description = fields.Text(
        string='Request Details',
        tracking=True
    )
    
    source = fields.Selection([
        ('website', 'Website Form'),
        ('phone', 'Phone Call'),
        ('email', 'Email'),
        ('walk_in', 'Walk-in'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('other', 'Other')
    ], string='Source', default='phone', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    
    state = fields.Selection([
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted to Lead'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', required=True, tracking=True)
    
    # CRM Integration
    lead_id = fields.Many2one(
        'crm.lead',
        string='Related Lead',
        readonly=True,
        copy=False,
        tracking=True
    )
    
    lead_count = fields.Integer(
        string='Lead Count',
        compute='_compute_lead_count'
    )
    
    # Expected Revenue (for conversion)
    expected_revenue = fields.Monetary(
        string='Expected Revenue',
        currency_field='currency_id',
        help='Estimated revenue for this request'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Timestamps
    contacted_date = fields.Datetime(
        string='Contacted On',
        readonly=True,
        tracking=True
    )
    
    converted_date = fields.Datetime(
        string='Converted On',
        readonly=True,
        tracking=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    notes = fields.Html(
        string='Internal Notes'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set sequence number"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('cater.customer.request') or _('New')
        return super().create(vals_list)

    @api.depends('lead_id')
    def _compute_lead_count(self):
        """Compute number of related leads"""
        for request in self:
            request.lead_count = 1 if request.lead_id else 0

    def action_contact(self):
        """Mark as contacted"""
        self.ensure_one()
        self.write({
            'state': 'contacted',
            'contacted_date': fields.Datetime.now()
        })
        self.message_post(body=_('Customer contacted'))

    def action_qualify(self):
        """Mark as qualified"""
        self.ensure_one()
        if self.state not in ['new', 'contacted']:
            raise UserError(_('Only new or contacted requests can be qualified.'))
        self.write({'state': 'qualified'})
        self.message_post(body=_('Request qualified'))

    def action_cancel(self):
        """Cancel request"""
        self.ensure_one()
        if self.state == 'converted':
            raise UserError(_('Cannot cancel a request that has been converted to a lead.'))
        self.write({'state': 'cancelled'})
        self.message_post(body=_('Request cancelled'))

    def action_create_lead(self):
        """
        Convert customer request to CRM lead with automatic tagging
        """
        self.ensure_one()
        
        if self.lead_id:
            raise UserError(_('This request has already been converted to a lead.'))
        
        # Get tags
        catering_tag = self.env.ref('cater.tag_catering_inquiry', raise_if_not_found=False)
        urgent_tag = self.env.ref('cater.tag_urgent', raise_if_not_found=False)
        high_value_tag = self.env.ref('cater.tag_high_value', raise_if_not_found=False)
        
        # Determine event type tag
        event_type_tag = None
        if self.event_type == 'wedding':
            event_type_tag = self.env.ref('cater.tag_wedding', raise_if_not_found=False)
        elif self.event_type == 'corporate':
            event_type_tag = self.env.ref('cater.tag_corporate_event', raise_if_not_found=False)
        elif self.event_type in ['birthday', 'anniversary', 'other']:
            event_type_tag = self.env.ref('cater.tag_private_party', raise_if_not_found=False)
        
        # Collect all tags
        tag_ids = []
        if catering_tag:
            tag_ids.append(catering_tag.id)
        if event_type_tag:
            tag_ids.append(event_type_tag.id)
        if urgent_tag and self.priority in ['2', '3']:
            tag_ids.append(urgent_tag.id)
        if high_value_tag and self.budget_range == 'above_10000':
            tag_ids.append(high_value_tag.id)
        
        # Get catering team
        catering_team = self.env.ref('cater.crm_team_catering', raise_if_not_found=False)
        
        # Get first stage
        first_stage = self.env.ref('cater.stage_lead_inquiry', raise_if_not_found=False)
        
        # Prepare lead description
        description_parts = []
        if self.description:
            description_parts.append(f"<p><strong>Request Details:</strong><br/>{self.description}</p>")
        
        description_parts.append(f"<p><strong>Event Information:</strong></p>")
        description_parts.append(f"<ul>")
        if self.event_type:
            description_parts.append(f"<li>Event Type: {dict(self._fields['event_type'].selection).get(self.event_type)}</li>")
        if self.event_date:
            description_parts.append(f"<li>Event Date: {self.event_date}</li>")
        if self.guest_count:
            description_parts.append(f"<li>Guest Count: {self.guest_count}</li>")
        if self.service_type:
            description_parts.append(f"<li>Service Type: {dict(self._fields['service_type'].selection).get(self.service_type)}</li>")
        if self.venue_location:
            description_parts.append(f"<li>Venue: {self.venue_location}</li>")
        if self.budget_range:
            description_parts.append(f"<li>Budget Range: {dict(self._fields['budget_range'].selection).get(self.budget_range)}</li>")
        description_parts.append(f"</ul>")
        
        # Add package and menu information
        if self.package_id or self.menu_item_ids:
            description_parts.append(f"<p><strong>Package & Menu Preferences:</strong></p>")
            description_parts.append(f"<ul>")
            if self.package_id:
                description_parts.append(f"<li>Interested Package: {self.package_id.name}</li>")
            if self.menu_item_ids:
                menu_names = ', '.join(self.menu_item_ids.mapped('name'))
                description_parts.append(f"<li>Interested Menu Items: {menu_names}</li>")
            description_parts.append(f"</ul>")
        
        if self.notes:
            description_parts.append(f"<p><strong>Internal Notes:</strong><br/>{self.notes}</p>")
        
        # Estimate expected revenue based on budget range
        revenue_estimate = 0.0
        if self.expected_revenue:
            revenue_estimate = self.expected_revenue
        elif self.budget_range:
            budget_map = {
                'under_1000': 750.0,
                '1000_3000': 2000.0,
                '3000_5000': 4000.0,
                '5000_10000': 7500.0,
                'above_10000': 15000.0,
            }
            revenue_estimate = budget_map.get(self.budget_range, 0.0)
        
        # Create lead
        lead_vals = {
            'name': f"{self.partner_id.name} - {dict(self._fields['event_type'].selection).get(self.event_type, 'Event')}",
            'partner_id': self.partner_id.id,
            'email_from': self.partner_email,
            'phone': self.partner_phone,
            'type': 'opportunity',
            'user_id': self.user_id.id,
            'team_id': catering_team.id if catering_team else False,
            'stage_id': first_stage.id if first_stage else False,
            'tag_ids': [(6, 0, tag_ids)],
            'description': ''.join(description_parts),
            'priority': self.priority,
            'expected_revenue': revenue_estimate,
            'customer_request_id': self.id,
            'company_id': self.company_id.id,
            # Add catering-specific fields
            'event_date': self.event_date,
            'guest_count': self.guest_count,
            'venue_location': self.venue_location,
            # Add package and menu items
            'interested_package_id': self.package_id.id if self.package_id else False,
            'interested_menu_item_ids': [(6, 0, self.menu_item_ids.ids)] if self.menu_item_ids else False,
        }
        
        # Add date_deadline if event_date exists
        if self.event_date:
            lead_vals['date_deadline'] = self.event_date
        
        lead = self.env['crm.lead'].create(lead_vals)
        
        # Update request
        self.write({
            'lead_id': lead.id,
            'state': 'converted',
            'converted_date': fields.Datetime.now()
        })
        
        # Post message
        self.message_post(
            body=_('Converted to CRM Lead: <a href="#" data-oe-model="crm.lead" data-oe-id="%s">%s</a>') % (lead.id, lead.name)
        )
        
        _logger.info(f"Customer request {self.name} converted to lead {lead.name} with tags: {tag_ids}")
        
        # Return action to view the lead
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lead'),
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_lead(self):
        """View related lead"""
        self.ensure_one()
        if not self.lead_id:
            raise UserError(_('No lead has been created from this request yet.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lead'),
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
