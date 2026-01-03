# Package and Menu Items Integration in CRM Lifecycle

## Overview

This document describes the integration of package and menu item selection throughout the customer request → lead → booking conversion flow.

## Features Added

### 1. Customer Request Form

The customer request form now includes:

- **Interested Package**: A dropdown to select a package the customer is interested in
- **Interested Menu Items**: A multi-select field (tags widget) to select specific menu items

These selections help capture customer preferences during the initial inquiry stage.

### 2. CRM Lead Form

When a customer request is converted to a lead, the package and menu selections are transferred to the lead:

- **Interested Package**: Available in the lead form
- **Interested Menu Items**: Displayed as tags in the lead form

This allows sales reps to see customer preferences while working the lead through the pipeline.

### 3. Automatic Booking Population

When converting a lead to a booking, the system automatically:

#### If Package Selected:

- Sets the `package_id` on the booking
- The booking's onchange handler automatically populates menu items and services from the package
- This provides a complete starting point for the booking

#### If Menu Items Selected (No Package):

- Creates menu line items for each selected menu item
- Sets quantity based on guest count from the lead
- Adds a note "From customer interest" to track origin

## Usage Workflow

### For Sales Staff

1. **Customer Request Stage**

   - Customer inquires about an event
   - Sales rep creates customer request
   - Select event details (date, guest count, venue)
   - **NEW**: Select a package if customer mentions interest in a specific package
   - **NEW**: Select menu items if customer mentions specific dishes/items they want
   - Convert request to lead

2. **CRM Lead Stage**

   - Work the lead through pipeline stages
   - Package and menu preferences are visible on the lead form
   - Use this information during customer consultations
   - When lead is won, convert to booking

3. **Booking Creation**
   - System automatically creates booking with:
     - All event details from lead
     - Package (if selected) which auto-populates menu and services
     - OR individual menu items (if no package selected)
   - Sales rep can then adjust quantities, add/remove items
   - Finalize pricing and confirm with customer

### For Customers (Portal)

- Customers can see their package/menu preferences in the portal
- When booking is created, they can review the selected items
- Transparent view of what they initially requested vs. final booking

## Technical Implementation

### Models Extended

#### cater.customer.request

```python
package_id = fields.Many2one('cater.package', string='Interested Package')
menu_item_ids = fields.Many2many('cater.menu.item', string='Interested Menu Items')
```

#### crm.lead

```python
interested_package_id = fields.Many2one('cater.package', string='Interested Package')
interested_menu_item_ids = fields.Many2many('cater.menu.item', string='Interested Menu Items')
```

### Conversion Logic

#### Request → Lead

In `customer_request.py`:

```python
lead_vals = {
    # ... other fields ...
    'interested_package_id': self.package_id.id if self.package_id else False,
    'interested_menu_item_ids': [(6, 0, self.menu_item_ids.ids)] if self.menu_item_ids else False,
}
```

Also adds package and menu information to lead description for easy reference.

#### Lead → Booking

In `crm_lead_extend.py`:

```python
# Add package if selected
if self.interested_package_id:
    booking_vals['package_id'] = self.interested_package_id.id

booking = self.env['cater.event.booking'].create(booking_vals)

# Add menu items if no package (avoid duplicates)
if self.interested_menu_item_ids and not self.interested_package_id:
    menu_line_vals = []
    for menu_item in self.interested_menu_item_ids:
        menu_line_vals.append((0, 0, {
            'menu_item_id': menu_item.id,
            'quantity': self.guest_count if self.guest_count else 1,
            'notes': 'From customer interest'
        }))
    booking.write({'menu_line_ids': menu_line_vals})
```

## Benefits

1. **Customer Preferences Captured**: No information loss during conversion process
2. **Faster Booking Creation**: Pre-populated with customer's initial interests
3. **Better Customer Experience**: Shows we listened to their initial requests
4. **Sales Efficiency**: Less back-and-forth to confirm preferences
5. **Audit Trail**: Clear tracking of what customer originally requested vs. final booking

## Best Practices

1. **Use Packages for Standard Offerings**: If customer mentions a package by name, select it
2. **Use Menu Items for Custom Requests**: For à la carte or custom selections
3. **Don't Over-Commit**: These are "interested" fields, not final commitments
4. **Review Before Finalizing**: Always review auto-populated items with customer before confirming
5. **Update as Needed**: Customer preferences may change - the booking is the source of truth

## Field Relationships

```
Customer Request
    └── package_id → cater.package
    └── menu_item_ids → cater.menu.item (many2many)
        ↓
    CRM Lead
        └── interested_package_id → cater.package
        └── interested_menu_item_ids → cater.menu.item (many2many)
            ↓
        Event Booking
            └── package_id → cater.package
            └── menu_line_ids → cater.booking.menu.line
                └── menu_item_id → cater.menu.item
```

## Configuration

No additional configuration required. The fields are available immediately after module upgrade.

### Security

- Same security rules apply as parent models
- Sales staff can view and edit package/menu selections
- Portal users can view their selections in request/booking portals

## Troubleshooting

### Package not transferring to booking

- Check that `interested_package_id` is set on the lead
- Verify package record still exists and is active
- Check booking's package onchange is triggering

### Menu items not appearing on booking

- Ensure no package is selected (package takes precedence)
- Verify `interested_menu_item_ids` has values on lead
- Check menu items are active and not archived

### Duplicate menu items on booking

- If package is selected, don't manually add menu items
- Package onchange will automatically populate items
- Remove duplicates manually if they occur

## Future Enhancements

Potential improvements for future versions:

- Smart suggestions based on event type and guest count
- Popular package recommendations
- Menu item compatibility checking
- Automatic quantity adjustments based on guest count changes
- Package customization (add/remove items from standard package)

## Related Documentation

- [CRM_CLIENT_LIFECYCLE.md](./CRM_CLIENT_LIFECYCLE.md) - Complete CRM integration guide
- [PACKAGES.md](./PACKAGES.md) - Package management documentation
- Main booking documentation for menu and service line management
