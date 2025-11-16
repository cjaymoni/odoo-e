# Kanban Views Implementation Guide

## Overview

This guide documents the implementation of kanban views with contextual actions and custom buttons for the Catering Management module.

## Event Bookings Kanban View

### Features Implemented

#### 1. **Visual Layout**

- **Card-based design** with color-coding support
- **State-based grouping** - Drag and drop bookings between workflow states:
  - Draft (Blue/Info)
  - Confirmed (Green/Success)
  - In Progress (Orange/Warning)
  - Completed (Green/Success)
  - Cancelled (Red/Danger)

#### 2. **Progress Bar**

- Visual indicator at the top showing distribution of bookings across states
- Color-coded to match state colors

#### 3. **Event Type Badges**

- Color-coded badges for quick event type identification:
  - Wedding → Red badge
  - Corporate → Blue badge
  - Birthday → Yellow badge
  - Anniversary → Cyan badge
  - Other types → Gray badge

#### 4. **Information Display**

Each kanban card shows:

- **Booking Reference** (name)
- **Event Name**
- **Customer** (with user icon)
- **Event Date** (calendar icon)
- **Venue** (map marker icon)
- **Guest Count** (users icon)
- **Total Amount** (highlighted in green)
- **Balance Due** (warning alert if > 0)

#### 5. **Contextual Actions** (Dropdown Menu)

Three-dot menu in top-right corner with:

**Standard Actions:**

- Edit
- Delete
- Change card color (color picker)

**State-based Actions:**

- **Send Confirmation** - Available when state = confirmed
- **View Invoice** - Available for confirmed, in_progress, completed
- **Create Invoice** - Available for confirmed bookings with balance due

#### 6. **Quick Action Buttons** (State-based)

Located at the bottom-right of each card:

| Current State   | Button   | Action             | Style            |
| --------------- | -------- | ------------------ | ---------------- |
| Draft           | Confirm  | action_confirm     | Green (success)  |
| Confirmed       | Start    | action_start_event | Orange (warning) |
| In Progress     | Complete | action_complete    | Blue (primary)   |
| Draft/Confirmed | Cancel   | action_cancel      | Red (danger)     |

#### 7. **Drag & Drop Functionality**

- Drag bookings between state columns to change their status
- Quick visual workflow management

## File Changes

### 1. `views/events_views.xml`

**Added:**

- New kanban view record: `catering_event_booking_kanban_view`
- Updated action view_mode: `kanban,list,form` (kanban is now default)
- Updated "Today's Events" action with kanban support

**Kanban Structure:**

```xml
<kanban default_group_by="state" class="o_kanban_small_column" quick_create="false">
    <!-- Fields -->
    <!-- Progress bar -->
    <!-- Card template with:
         - Dropdown menu (contextual actions)
         - Card header (name, event name, type badge)
         - Card body (customer, date, venue, guests, amount, balance)
         - Quick action buttons (state-based)
    -->
</kanban>
```

### 2. `models/event_booking.py`

**Added:**

- `color` field (Integer) - For kanban color-coding
  ```python
  color = fields.Integer('Color Index', default=0)
  ```

## How to Use

### 1. **Upgrade the Module**

```bash
docker compose run --rm odoo python3 -m odoo -c odoo.conf -u cater -d catering_db --stop-after-init
```

### 2. **Restart Odoo**

```bash
docker compose restart odoo
```

### 3. **Access Kanban View**

1. Navigate to: **Catering → Bookings → All Bookings**
2. Click the kanban view icon (grid icon) in the top-right
3. You'll see columns for each state: Draft, Confirmed, In Progress, Completed, Cancelled

### 4. **Working with Kanban**

#### **Change State via Drag & Drop:**

- Drag a booking card to a different column
- The state will update automatically

#### **Use Quick Action Buttons:**

- Click the button at the bottom of the card
- State transitions are enforced (can't skip stages)

#### **Access Contextual Menu:**

- Click the three dots (⋮) in the top-right of any card
- Select from available actions based on booking state

#### **Color Coding:**

- Click three dots → Select a color from the color picker
- Adds visual distinction to important bookings

#### **Create New Booking:**

- Click "Create" button
- Note: Quick create is disabled to ensure all required fields are filled

## Customization Options

### Change Default Grouping

Edit `views/events_views.xml`:

```xml
<!-- Current: Group by state -->
<kanban default_group_by="state">

<!-- Alternative options: -->
<kanban default_group_by="event_type">  <!-- Group by event type -->
<kanban default_group_by="partner_id">  <!-- Group by customer -->
<kanban default_group_by="event_date">  <!-- Group by date -->
```

### Add More Quick Actions

Edit the kanban template in `views/events_views.xml`:

```xml
<button name="your_method_name" type="object"
        class="btn btn-sm btn-primary"
        t-if="record.state.raw_value == 'your_condition'"
        title="Button Tooltip">
    <i class="fa fa-icon-name"/> Button Text
</button>
```

### Add More Contextual Menu Items

Edit the dropdown menu section:

```xml
<a name="action_method_name" type="object" class="dropdown-item"
   t-if="record.state.raw_value == 'your_condition'">
    <i class="fa fa-icon"/> Menu Item Text
</a>
```

### Customize Card Colors

The progress bar colors are defined in:

```xml
<progressbar field="state" colors='{
    "draft": "info",      <!-- Blue -->
    "confirmed": "success", <!-- Green -->
    "in_progress": "warning", <!-- Orange -->
    "completed": "success",   <!-- Green -->
    "cancelled": "danger"     <!-- Red -->
}'/>
```

## Required Methods

The following methods must exist in `models/event_booking.py` for the buttons to work:

✅ **Implemented:**

- `action_confirm()` - Transition draft → confirmed
- `action_start_event()` - Transition confirmed → in_progress
- `action_complete()` - Transition in_progress → completed
- `action_cancel()` - Transition to cancelled

⚠️ **Optional (may need implementation):**

- `action_send_confirmation()` - Send confirmation email/SMS
- `action_view_invoice()` - Open related invoice(s)
- `action_create_invoice()` - Generate invoice from booking

## Mobile Responsiveness

The kanban view is mobile-friendly:

- Cards stack vertically on small screens
- Touch-friendly buttons and controls
- Responsive column layout

## Performance Considerations

1. **Indexes Added** (already in model):

   - `idx_cater_booking_state` - Fast state-based queries
   - `idx_cater_booking_event_date` - Fast date filtering
   - `idx_cater_booking_partner_state` - Combined partner/state queries

2. **Computed Fields**:

   - All monetary fields are stored for fast kanban loading
   - No heavy computations in kanban view

3. **Quick Create Disabled**:
   - Prevents incomplete records
   - Ensures data quality

## Best Practices

### 1. **Use Color Coding Strategically**

- Red: Urgent or high-priority bookings
- Yellow: Bookings needing attention
- Green: Confirmed and paid bookings
- Blue: Standard bookings

### 2. **Workflow Management**

- Use kanban for quick status updates
- Use form view for detailed editing
- Use list view for batch operations

### 3. **Filtering**

- Combine kanban with search filters
- Example: Filter "Today's Events" and view in kanban

### 4. **Team Collaboration**

- Assign colors to team members
- Use state columns for workflow stages
- Track progress with progress bar

## Troubleshooting

### Kanban view not appearing?

1. Check module is upgraded: `Settings → Apps → Cater → Upgrade`
2. Clear browser cache
3. Check XML file has no syntax errors

### Buttons not working?

1. Verify methods exist in `event_booking.py`
2. Check method names match exactly
3. Review server logs for errors

### Drag & drop not working?

1. Ensure `default_group_by` is set
2. Verify user has write permissions
3. Check state field is editable

### Cards look wrong?

1. Clear Odoo assets: `Settings → Technical → Clear Assets`
2. Refresh browser with Ctrl+F5
3. Check CSS classes are correct

## Next Steps

Consider adding kanban views for:

1. **Menu Items** - Already has kanban for items, extend with actions
2. **Services** - Visual service catalog
3. **Feedback** - Track feedback by rating/status
4. **WhatsApp Logs** - Monitor message status

## Support

For questions or issues:

1. Check Odoo 18 kanban view documentation
2. Review `odoo/addons/*/views/*_views.xml` for examples
3. Test in developer mode with logging enabled

---

**Created:** 2025
**Module:** Catering Management v2.0
**Odoo Version:** 18.0 Enterprise
