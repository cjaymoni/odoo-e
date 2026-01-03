# CRM & Client Lifecycle Integration

## Overview

The Catering Management System integrates with Odoo CRM to provide a complete client lifecycle management solution. This integration enables seamless tracking from initial inquiry through lead qualification to final event booking, ensuring no opportunity is lost.

## Architecture

### Three-Stage Lifecycle

```
Customer Request → CRM Lead/Opportunity → Event Booking → Invoice
     (Inquiry)      (Sales Pipeline)        (Confirmed)     (Payment)
```

### Data Flow

1. **Customer Request**: Initial inquiry capture
2. **Lead Creation**: Automated conversion with tagging
3. **Lead Progression**: Through custom sales stages
4. **Booking Conversion**: Transfer to event management
5. **Invoice Generation**: Financial tracking

## Features

### 1. Customer Request Management

- Capture initial inquiries before CRM entry
- Qualify requests before lead creation
- Track request source and priority
- Estimate expected revenue
- Multiple contact states: New → Contacted → Qualified → Converted

### 2. Custom CRM Pipeline

Pre-configured stages specific to catering sales:

- **Inquiry**: Initial contact received
- **Consultation Scheduled**: Meeting arranged
- **Proposal Sent**: Quote provided
- **Negotiation**: Terms discussion
- **Won**: Deal closed
- **Lost**: Opportunity lost

### 3. Automated Lead Tagging

Intelligent tagging based on:

- Request type (automatic "Catering Inquiry" tag)
- Event type (Wedding, Corporate, Private Party)
- Budget range (High Value for >₵5,000)
- Urgency (Urgent for events within 7 days)
- Expected revenue

### 4. Lead-to-Booking Conversion

One-click conversion that transfers:

- Customer information
- Event details (date, guests, venue)
- Expected revenue → Deposit calculation
- Notes and description
- Activities and follow-ups
- Sales representative assignment

### 5. Bidirectional Navigation

Smart buttons for easy navigation:

- Request ↔ Lead
- Lead ↔ Booking
- Booking ↔ Invoice
- Complete audit trail

## User Guide

### Creating a Customer Request

#### Step 1: Access Customer Requests

Navigate to: **Event Planning → Bookings → Customer Requests**

#### Step 2: Create New Request

1. Click **New**
2. Fill in customer information:
   - **Customer**: Select or create partner
   - **Event Type**: Wedding, Corporate, etc.
   - **Event Date**: Requested date
   - **Expected Guests**: Number of attendees
   - **Service Type**: Catering only, Full service, etc.
   - **Budget Range**: Select range
3. Add **Request Details**: Special requirements, preferences
4. Set **Priority**: Low, Normal, High, Urgent
5. Assign **Responsible User**
6. **Save**

#### Step 3: Progress the Request

- **Mark Contacted**: After initial contact
- **Qualify**: When request meets criteria
- **Convert to Lead**: Creates CRM opportunity

### Converting Request to Lead

#### Automatic Conversion

When you click **Convert to Lead**:

1. **Lead Created** with:

   - Name: "Customer Name - Event Type"
   - Type: Opportunity
   - Team: Catering Sales
   - Stage: Inquiry

2. **Automatic Tags Applied**:

   - "Catering Inquiry" (always)
   - Event type tag (Wedding/Corporate/Private Party)
   - "Urgent Request" (if event within 7 days)
   - "High Value" (if budget >₵5,000)

3. **Information Transferred**:

   - Customer contact details
   - Event information
   - Request description
   - Expected revenue estimate
   - Internal notes

4. **Request Updated**:
   - State: Converted
   - Link to lead maintained
   - Conversion timestamp recorded

#### View Created Lead

Click the **Lead** smart button to view the CRM opportunity.

### Managing Leads

#### Accessing Leads

Navigate to: **CRM → My Pipeline** or **Sales → Leads**

#### Lead Stages

Progress leads through stages by dragging in kanban view or changing stage:

1. **Inquiry**:

   - Review request details
   - Contact customer
   - Understand requirements

2. **Consultation Scheduled**:

   - Schedule meeting activity
   - Prepare sample menus
   - Discuss options

3. **Proposal Sent**:

   - Create quotation
   - Send via email
   - Set follow-up activity

4. **Negotiation**:

   - Discuss pricing
   - Adjust services
   - Address concerns

5. **Won**:

   - Deal closed
   - Ready for booking conversion
   - Receive notification

6. **Lost**:
   - Record lost reason
   - Archive for future reference

#### Lead Information

**Catering-Specific Fields**:

- **Event Date**: Requested event date
- **Expected Guests**: Number of attendees
- **Venue/Location**: Event venue
- **Expected Revenue**: Estimated booking value
- **Customer Request**: Link to original request

**Standard CRM Fields**:

- **Customer**: Partner record
- **Email/Phone**: Contact information
- **Sales Team**: Catering Sales
- **Assigned To**: Sales representative
- **Priority**: Star rating
- **Tags**: Automated and manual tags
- **Activities**: Follow-up tasks
- **Notes**: Internal discussion

### Converting Lead to Booking

#### Prerequisites

- Lead must be in **Won** stage
- Customer must be selected
- Event information should be filled

#### Conversion Process

1. **Mark Lead as Won**:

   - Move to "Won" stage
   - System creates activity: "Convert Lead to Booking"

2. **Click Convert to Booking**:

   - Button appears in lead form header
   - Only visible when lead is won

3. **Booking Created** with:

   - **Event Name**: From lead name
   - **Customer**: From lead partner
   - **Event Date**: From lead event_date or deadline
   - **Guest Count**: From lead guest_count
   - **Venue**: From lead venue_location
   - **State**: Draft (ready for menu/service selection)
   - **Deposit**: 20% of expected revenue
   - **Notes**: Complete lead history
   - **Assigned To**: Same user as lead
   - **Lead Link**: Maintained for tracking

4. **Activities Copied**:
   All scheduled activities transfer to booking

5. **Navigation**:
   System opens booking form automatically
   Or use **Booking** smart button on lead

#### After Conversion

**On Lead**:

- Booking link maintained
- Smart button shows booking
- Lead remains for reporting

**On Booking**:

- Lead link maintained
- Smart button shows lead
- Ready for menu/service selection

**Next Steps**:

1. Add menu items
2. Add services
3. Set pricing
4. Confirm booking
5. Generate invoice

### Complete Lifecycle Example

#### Scenario: Wedding Inquiry

**Day 1 - Initial Contact**:

```
Phone call received from bride
→ Create Customer Request
   - Event Type: Wedding
   - Date: 3 months away
   - Guests: 150
   - Budget: ₵8,000-₵12,000
   - Priority: High
→ Save and Mark Contacted
```

**Day 2 - Qualification**:

```
Follow-up call completed
Requirements clarified
Budget confirmed
→ Click Qualify
→ Click Convert to Lead
```

**System Actions**:

```
✓ Lead created: "Mary Osei - Wedding"
✓ Stage: Inquiry
✓ Tags: Catering Inquiry, Wedding, High Value
✓ Expected Revenue: ₵10,000 (from budget range)
✓ Team: Catering Sales
✓ Activity: Contact customer (auto-created)
```

**Day 5 - Consultation**:

```
Meeting scheduled
→ Move to "Consultation Scheduled"
→ Create activity: "Prepare wedding package options"
→ Add notes about preferences
```

**Day 10 - Proposal**:

```
Quotation prepared
→ Move to "Proposal Sent"
→ Email sent with menus
→ Follow-up activity scheduled
```

**Day 15 - Negotiation**:

```
Customer requests adjustments
→ Move to "Negotiation"
→ Update expected revenue: ₵11,500
→ Modify proposal
```

**Day 20 - Won**:

```
Customer agrees to terms
→ Move to "Won" stage
→ Activity created: "Convert Lead to Booking"
→ Click Convert to Booking
```

**System Actions**:

```
✓ Booking created: "Mary Osei Wedding - [Date]"
✓ Deposit calculated: ₵2,300 (20% of ₵11,500)
✓ All notes copied
✓ Activities transferred
✓ State: Draft
```

**Day 21 - Booking Setup**:

```
→ Add menu items (buffet selections)
→ Add services (decoration, DJ, photographer)
→ Review total: ₵11,650
→ Confirm Booking
```

**Day 22 - Invoice**:

```
→ Click Create Invoice
→ Invoice generated with 15% VAT
→ Total: ₵13,397.50
→ Email to customer
```

**Event Day - Completion**:

```
→ Start Event (status: In Progress)
→ Complete Event (status: Completed)
→ Collect feedback
→ Record final payment
```

## Automated Actions

### 1. High-Value Lead Assignment

**Trigger**: Lead created or updated
**Condition**: Expected revenue ≥ ₵5,000 AND no assignee
**Action**: Assign to Sales Manager
**Message**: "Auto-assigned to Sales Manager due to high expected revenue."

### 2. Urgent Lead Tagging

**Trigger**: Lead created or updated
**Condition**: Event date exists
**Logic**: If event within 7 days → Add "Urgent" tag
**Message**: "Tagged as Urgent - Event is within 7 days."

### 3. Urgent Tag Removal

**Trigger**: Daily (scheduled action)
**Condition**: Event date has passed
**Action**: Remove "Urgent" tag
**Message**: "Removed Urgent tag - Event date has passed."

### 4. Won Lead Notification

**Trigger**: Lead stage changes to Won
**Action**:

- Create activity: "Convert Lead to Booking"
- Assigned to: Lead owner
- Message: "Lead marked as Won! Next step: Convert to Event Booking."

### 5. High-Value Tagging

**Trigger**: Lead created or updated
**Condition**: Expected revenue ≥ ₵5,000
**Action**: Add "High Value (>$5000)" tag
**Message**: "Tagged as High Value - Expected revenue exceeds ₵5,000."

## Reporting & Analytics

### Key Metrics

**Customer Requests**:

- Total requests by period
- Conversion rate to leads
- Average time to conversion
- Request source breakdown
- Budget distribution

**CRM Pipeline**:

- Leads by stage
- Conversion rate per stage
- Average cycle time
- Expected revenue by stage
- Win/loss ratio

**Lead-to-Booking**:

- Conversion rate
- Revenue accuracy (expected vs actual)
- Time from lead to booking
- Revenue by event type

### Available Reports

Navigate to: **CRM → Reporting**

**Pipeline Analysis**:

- Opportunities by stage
- Expected revenue forecast
- Team performance
- Won/lost analysis

**Custom Reports**:

- Catering leads dashboard
- Event booking funnel
- Revenue pipeline
- Conversion metrics

### Filters & Views

**Customer Requests**:

- Group by: Status, Event Type, Budget, Source
- Filter by: New, Qualified, My Requests, Priority

**CRM Leads**:

- Group by: Stage, Team, Assigned To, Tags
- Filter by: My Pipeline, Urgent, High Value, Event Type
- Kanban: Drag-and-drop stage management

## Configuration

### CRM Team Setup

Navigate to: **CRM → Configuration → Sales Teams**

**Catering Sales Team**:

- **Name**: Catering Sales
- **Use Leads**: Enabled
- **Use Opportunities**: Enabled
- **Alias**: catering.leads@yourcompany.com
- **Members**: Add sales staff
- **Stages**: Custom catering stages

### Lead Stages

Navigate to: **CRM → Configuration → Stages**

Edit existing or create new stages:

- **Sequence**: Order in pipeline
- **Team**: Catering Sales
- **Fold**: Hide in kanban
- **Is Won**: Mark as closed-won

### Tags Management

Navigate to: **CRM → Configuration → Tags**

Available tags:

- Catering Inquiry (blue)
- Corporate Event (green)
- Wedding (purple)
- Private Party (yellow)
- High Value (orange)
- Urgent Request (red)

Create custom tags as needed for:

- Service types
- Package tiers
- Geographic regions
- Marketing campaigns

### Automated Actions

Navigate to: **Settings → Technical → Automation → Automated Actions**

Review and customize:

- Enable/disable actions
- Modify conditions
- Change assignments
- Update messaging

## Best Practices

### 1. Customer Request Management

- **Capture Early**: Log every inquiry
- **Qualify Quickly**: Move to leads within 24 hours
- **Track Source**: Important for marketing ROI
- **Estimate Revenue**: Helps with prioritization
- **Assign Properly**: Right person for request type

### 2. Lead Progression

- **Update Regularly**: Keep stages current
- **Use Activities**: Schedule all follow-ups
- **Add Notes**: Document all interactions
- **Update Revenue**: Adjust as negotiations progress
- **Tag Appropriately**: Helps with filtering and reporting

### 3. Conversion Timing

- **Convert When Won**: Only convert closed-won leads
- **Verify Information**: Check all details before converting
- **Add Context**: Include all requirements in booking notes
- **Schedule Activities**: Plan next steps during conversion

### 4. Data Quality

- **Complete Profiles**: Fill all customer information
- **Accurate Dates**: Essential for urgency tracking
- **Realistic Revenue**: Affects forecasting and assignment
- **Proper Tagging**: Improves searchability

### 5. Team Collaboration

- **Follow Activities**: Complete tasks on time
- **Use Chatter**: Internal communication
- **Log Calls**: Record all customer interactions
- **Share Knowledge**: Document successful approaches

## Troubleshooting

### Request Won't Convert to Lead

**Problem**: "Convert to Lead" button not working

**Solutions**:

1. **Check state**: Must be "Qualified"
2. **Verify customer**: Partner must be selected
3. **Check permissions**: User needs CRM rights
4. **Review logs**: Check for errors in Odoo logs

### Lead Won't Convert to Booking

**Problem**: "Convert to Booking" button disabled

**Solutions**:

1. **Check stage**: Lead must be in "Won" stage
2. **Verify customer**: Partner_id must be set
3. **Check permissions**: User needs booking creation rights
4. **Mark as won**: Move to Won stage first

### Missing Tags

**Problem**: Automatic tags not applied

**Solutions**:

1. **Check automation**: Settings → Automated Actions
2. **Verify XML IDs**: Tags must exist in database
3. **Review conditions**: Check filter domains
4. **Trigger manually**: Edit and save lead to re-trigger

### Smart Buttons Not Showing

**Problem**: Can't see related records

**Solutions**:

1. **Refresh page**: F5 or Ctrl+R
2. **Check links**: Verify lead_id/booking_id fields
3. **Review permissions**: User needs access to related model
4. **Save record**: Computed fields need save

## Security & Permissions

### Required Access Rights

**Customer Requests**:

- **Manager**: Full access (create, read, write, delete)
- **Staff**: Create, read, write
- **Client**: None (internal tool)

**CRM Leads**:

- **Manager**: Full access to all leads
- **Sales Person**: Own leads + team leads
- **Sales Team Leader**: Team leads only

**Event Bookings**:

- **Manager**: All bookings
- **Staff**: Own bookings
- **Client**: Own bookings (portal)

### Recommended Setup

**Sales Team**:

- Create customer requests
- Convert to leads
- Manage own leads
- Create bookings from leads

**Sales Manager**:

- All sales team permissions
- Assign leads
- Modify stages
- Delete records
- Configure automation

**Administrator**:

- Full system access
- Configure CRM
- Manage teams
- Setup automation

## Integration Points

### Email Integration

- Create leads from email to catering.leads@yourcompany.com
- Email gateway setup in CRM settings
- Automatic lead assignment

### WhatsApp Integration

- Send notifications at key stages
- Update customer on progress
- Automated booking confirmations

### Calendar Integration

- Activities appear in calendar
- Event dates synchronized
- Meeting scheduling

### Accounting Integration

- Expected revenue in forecasts
- Invoice generation from bookings
- Payment tracking

## API & Automation

### Creating Customer Request (Python)

```python
# Create customer request
request = env['cater.customer.request'].create({
    'partner_id': partner_id,
    'event_type': 'wedding',
    'event_date': '2026-06-15',
    'guest_count': 150,
    'service_type': 'full_service',
    'budget_range': '5000_10000',
    'description': 'Wedding reception at Hotel venue',
    'source': 'website',
    'priority': '2',
    'expected_revenue': 8000.0,
})

# Progress states
request.action_contact()
request.action_qualify()

# Convert to lead
lead = request.action_create_lead()
```

### Converting Lead to Booking (Python)

```python
# Get lead
lead = env['crm.lead'].browse(lead_id)

# Mark as won (if not already)
won_stage = env.ref('cater.stage_lead_won')
lead.stage_id = won_stage

# Convert to booking
booking = lead.action_convert_to_booking()

# Returns dict with booking action
# Access booking: booking['res_id']
```

### Searching & Filtering

```python
# Get high-value leads
high_value_leads = env['crm.lead'].search([
    ('expected_revenue', '>=', 5000),
    ('stage_id.is_won', '=', False),
])

# Get urgent requests
urgent_requests = env['cater.customer.request'].search([
    ('priority', '=', '3'),
    ('state', 'not in', ['converted', 'cancelled']),
])

# Get converted bookings
converted_bookings = env['cater.event.booking'].search([
    ('lead_id', '!=', False),
    ('state', '=', 'confirmed'),
])
```

## Performance Optimization

### Database Indexes

Automatic indexes created on:

- customer_request: event_date, state, partner_id
- crm_lead: event_date, expected_revenue
- event_booking: lead_id

### Search Optimization

- Use filters instead of manual search
- Leverage group_by for analysis
- Archive old records regularly

### Automation Efficiency

- Time-based actions run daily only
- Filter domains optimize queries
- Avoid complex computations in automation

## Future Enhancements

### Planned Features

- **Email Templates**: Automated emails per stage
- **SMS Integration**: Text message notifications
- **Proposal Generator**: PDF quotes from leads
- **Customer Portal**: Self-service request submission
- **Analytics Dashboard**: Real-time metrics
- **AI Lead Scoring**: Predictive win probability
- **Calendar Booking**: Venue availability checking
- **Social Media**: Lead capture from Facebook/Instagram

### Customization Options

- Add custom fields to request/lead
- Create additional stages
- Define new automated actions
- Build custom reports
- Integrate external systems

## Support & Resources

### Documentation

- [Multi-Currency Pricing](MULTI_CURRENCY_PRICING.md)
- [Accounting & VAT Integration](ACCOUNTING_VAT_INTEGRATION.md)
- [Multi-Company Setup](MULTI_COMPANY_IMPLEMENTATION.md)

### Odoo Resources

- [CRM Documentation](https://www.odoo.com/documentation/18.0/applications/sales/crm.html)
- [Automation Guide](https://www.odoo.com/documentation/18.0/developer/reference/backend/actions.html)
- [CRM Best Practices](https://www.odoo.com/slides/crm-27)

### Getting Help

1. Review this documentation
2. Check Odoo logs: Settings → Technical → Logging
3. Test in safe mode (disable customizations)
4. Contact system administrator
5. Odoo support (Enterprise users)

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Module**: cater (Catering Management System)  
**Odoo Version**: 18.0 Enterprise  
**Dependencies**: crm, sale, account, mail
