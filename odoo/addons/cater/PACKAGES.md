# 📦 Catering Packages - Feature Documentation

## Overview

The Catering Packages feature allows you to create pre-configured bundles of menu items and services that can be quickly applied to event bookings. This streamlines the booking process, ensures consistency, and makes it easier to offer standardized catering options to clients.

## Key Benefits

- **Faster Booking Creation**: Select a package and auto-populate menu items and services instantly
- **Consistency**: Ensure the same items are included every time for specific event types
- **Easy Management**: Create, duplicate, and modify packages without affecting existing bookings
- **Flexible Pricing**: Support for per-person, fixed-price, or custom pricing models
- **Visual Marketing**: Add images to packages for better presentation
- **Date-Based Availability**: Control when packages are available for selection

---

## Package Structure

### Main Package Model (`cater.package`)

A package consists of:

- **Basic Information**: Name, description, category, event type
- **Pricing**: Three pricing methods (per person, fixed, custom)
- **Menu Items**: Multiple menu line items with quantities
- **Services**: Multiple service line items with quantities
- **Availability**: Date ranges and guest capacity limits
- **Visual**: Package image for marketing purposes

### Related Models

1. **Package Menu Line** (`cater.package.menu.line`)

   - Links menu items to packages
   - Defines quantity for each menu item
   - Stores unit price and calculates subtotals
   - Supports special notes

2. **Package Service Line** (`cater.package.service.line`)
   - Links services to packages
   - Defines quantity for each service
   - Stores unit price and calculates subtotals
   - Supports special notes

---

## Creating a Package

### Step 1: Navigate to Packages

1. Go to **Catering → Packages**
2. Click **Create** button

### Step 2: Basic Information

Fill in the package details:

- **Package Name**: e.g., "Corporate Lunch Package"
- **Description**: Detailed description of what's included
- **Category**: Wedding, Corporate, Birthday, Other
- **Event Type**: wedding, corporate_event, birthday, social_gathering, etc.
- **Company**: Select your company (multi-company support)

### Step 3: Pricing Configuration

Choose one of three pricing methods:

#### 1. Per Person Pricing

- Set a **Price Per Person** amount
- Specify **Minimum Guests** and **Maximum Guests**
- Total cost will be calculated based on guest count in booking

#### 2. Fixed Price

- Set a **Fixed Price** for the entire package
- Guest count doesn't affect the price
- Ideal for venue rentals or fixed-capacity events

#### 3. Custom Pricing

- Allows manual price adjustment per booking
- Provides flexibility for negotiated pricing

### Step 4: Add Menu Items

In the **Menu Items** tab:

1. Click **Add a line**
2. Select a menu item from dropdown
3. Enter quantity (portions/servings)
4. Unit price auto-fills from menu item
5. Subtotal is calculated automatically
6. Add optional notes for special preparation
7. Repeat for all menu items

### Step 5: Add Services

In the **Services** tab:

1. Click **Add a line**
2. Select a service from dropdown
3. Enter quantity needed
4. Unit price auto-fills from service
5. Subtotal is calculated automatically
6. Add optional notes for service details
7. Repeat for all services

### Step 6: Set Availability (Optional)

In the **Availability** tab:

- **Available From**: Start date for package availability
- **Available Until**: End date for package availability
- Leave blank for always-available packages

### Step 7: Add Package Image (Optional)

- Click on the camera icon placeholder
- Upload an image (recommended: 1200x800px)
- Image appears in kanban view for visual selection

### Step 8: Save

Click **Save** to create the package

---

## Using Packages in Event Bookings

### Method 1: During Booking Creation

1. Navigate to **Catering → Event Bookings**
2. Click **Create**
3. Fill in basic booking information:
   - Customer name
   - Event date
   - Event type
   - Venue details
4. Locate the **📦 Package Selection (Optional)** section
5. Click the dropdown and select your package
6. **Automatic Population**:
   - All menu items from package are added to Menu Items tab
   - All services from package are added to Services tab
   - Quantities are pre-filled from package
   - Event type syncs if package has specific type
7. **Customize** (if needed):
   - Edit quantities of any item
   - Add additional menu items or services
   - Remove items not needed for this booking
8. Continue with booking workflow

### Method 2: Add to Existing Booking

1. Open an existing booking in edit mode
2. Scroll to **📦 Package Selection (Optional)** section
3. Select a package from dropdown
4. Package items will be added to existing lines
5. Review and adjust as needed

---

## Package Views

### 1. Kanban View (Card View)

- **Visual Display**: Shows package image, name, and category badge
- **Quick Info**:
  - Pricing details (per person, fixed, or custom)
  - Guest capacity range
  - Number of active bookings using this package
- **Color Coding**: Category-based color badges
- **Actions**: Click card to view/edit package details

### 2. List View (Table View)

- **Sortable Columns**: Name, category, pricing method, created date
- **Drag & Drop**: Reorder packages using sequence handle
- **Bulk Actions**: Select multiple packages for batch operations
- **Filters**: Available in search panel

### 3. Form View (Detail View)

Organized in tabs:

- **Pricing**: Pricing method, amounts, guest limits
- **Menu Items**: Line items with quantities and prices
- **Services**: Service lines with quantities and prices
- **Description**: Full package description
- **Availability**: Date ranges and status

### 4. Search & Filters

Quick filters available:

- **My Packages**: Packages in your company
- **Active**: Currently available packages
- **Archived**: Deactivated packages
- **By Category**: Wedding, Corporate, Birthday, Other
- **By Type**: General or specific event types

---

## Package Management Features

### Duplicate Package

1. Open an existing package
2. Click **Action** menu (⚙️)
3. Select **Duplicate**
4. A new package is created with:
   - Name: "[COPY] Original Package Name"
   - All menu items and services copied
   - Same pricing and settings
5. Modify the copy as needed
6. Save the new package

### View Package Bookings

1. Open a package
2. Click **View Bookings** smart button (top right)
3. See all event bookings using this package
4. Navigate to any booking for details

### Archive/Restore Package

- **Archive**: Set package to inactive (won't appear in booking selection)
- **Restore**: Reactivate an archived package
- Archived packages don't affect existing bookings

---

## Pricing Methods Explained

### Per Person Pricing

**Use Case**: Most flexible for catering where cost scales with guests

**How It Works**:

- Package defines price per person (e.g., $50/person)
- Booking calculates: `price_per_person × guest_count`
- Example: 100 guests × $50 = $5,000 total

**Best For**:

- Buffet services
- Plated dinners
- Per-head catering

### Fixed Price

**Use Case**: Events with set costs regardless of attendance

**How It Works**:

- Package defines one fixed price (e.g., $2,500)
- Guest count doesn't affect price
- Total is always the fixed amount

**Best For**:

- Venue rentals
- Equipment packages
- Fixed-capacity events

### Custom Pricing

**Use Case**: Negotiated or variable pricing per client

**How It Works**:

- No predefined price in package
- Price is set manually in each booking
- Provides maximum flexibility

**Best For**:

- Enterprise clients
- Negotiated contracts
- Special circumstances

---

## Multi-Company Support

### Company Isolation

- Each package belongs to one company
- Users only see packages from their company
- Record rules enforce data separation

### Sharing Packages

- Packages cannot be shared across companies
- Duplicate packages for each company if needed
- Menu items and services must exist in target company

---

## Integration with Bookings

### Auto-Population Logic

When a package is selected:

1. **Clear Mode**: Existing menu/service lines are NOT cleared
2. **Addition Mode**: Package items are ADDED to current lines
3. **Price Inheritance**: Prices come from menu items/services, not package
4. **Quantity Transfer**: Quantities from package are applied
5. **Event Type Sync**: If package has specific event type, it updates booking

### Field Relationships

- **package_id**: Many2one link from booking to package
- **menu_line_ids**: One2many booking menu lines
- **service_line_ids**: One2many booking service lines

### Computed Fields

Package automatically calculates:

- **menu_total**: Sum of all menu item subtotals
- **service_total**: Sum of all service subtotals
- **estimated_cost**: Total package cost estimate
- **is_available**: Whether package is currently available
- **booking_count**: Number of bookings using this package

---

## Visual Indicators

### In Booking Form View

- **📦 Package Selection (Optional)** section prominently displayed
- Placeholder text: "Select a package to auto-fill menu and services..."
- Help text explains auto-population behavior

### In Booking Kanban View

- Blue info badge appears on cards using packages
- Shows: 📦 **Package:** [Package Name]
- Only visible when booking has a package assigned

### In Booking List View

- Package column available (optional toggle)
- Shows package name when assigned
- Empty when no package used

---

## Best Practices

### Naming Conventions

- Use descriptive names: "Corporate Lunch Package - 50-100 Guests"
- Include capacity in name for quick reference
- Add season/period if time-limited: "Summer Wedding Package 2025"

### Pricing Strategy

1. **Research Costs**: Calculate total cost of all items in package
2. **Add Margin**: Include profit margin in pricing
3. **Market Comparison**: Check competitor pricing
4. **Update Regularly**: Review and adjust prices periodically

### Menu Item Selection

- Include variety (appetizers, mains, desserts)
- Consider dietary restrictions
- Balance popular and premium items
- Set realistic quantities

### Service Selection

- Include essential services (staff, equipment)
- Bundle complementary services
- Consider setup/cleanup time
- Account for service duration

### Image Guidelines

- Use high-quality photos (minimum 1200x800px)
- Show actual food/service setup
- Professional styling recommended
- Keep consistent style across packages

### Availability Management

- Set dates for seasonal packages
- Archive outdated packages instead of deleting
- Create new versions for updated offerings
- Track performance with booking count

---

## Common Use Cases

### Wedding Packages

```
Package Name: "Elegant Wedding Reception - 100-150 Guests"
Category: Wedding
Event Type: wedding
Pricing: Per Person ($85/person)

Menu Items:
- Welcome Cocktails (1 per person)
- 3-Course Meal (1 per person)
- Wedding Cake (150 servings)
- Champagne Toast (1 per person)

Services:
- Event Coordinator (1 person, 8 hours)
- Waitstaff (10 persons, 6 hours)
- Bartender (2 persons, 6 hours)
- Table/Chair Setup (1 setup)
```

### Corporate Event Packages

```
Package Name: "Business Lunch Meeting - 20-30 Attendees"
Category: Corporate
Event Type: corporate_event
Pricing: Fixed Price ($1,200)

Menu Items:
- Continental Breakfast (30 servings)
- Coffee & Tea Service (30 servings)
- Lunch Buffet (30 servings)
- Afternoon Snacks (30 servings)

Services:
- AV Equipment Setup (1 setup)
- Meeting Room Setup (1 setup)
- Service Staff (2 persons, 4 hours)
```

### Birthday Packages

```
Package Name: "Kids Birthday Party - Up to 25 Children"
Category: Birthday
Event Type: birthday
Pricing: Fixed Price ($450)

Menu Items:
- Pizza (10 large pizzas)
- Juice Boxes (30 boxes)
- Birthday Cake (25 servings)
- Party Snacks (25 servings)

Services:
- Party Entertainment (1 person, 2 hours)
- Balloon Decoration (1 setup)
- Cleanup Service (1 service)
```

---

## Security & Access Control

### Access Rights by Role

#### Manager (Full Access)

- Create, read, write, delete all packages
- Access all companies' packages (if multi-company)
- Manage archived packages
- View all package statistics

#### Staff (Standard Access)

- Create, read, write packages in their company
- Cannot delete packages
- View package bookings
- Duplicate packages

#### Client (Read-Only)

- Read packages in their company
- View package details
- Cannot create or modify packages
- Used for customer portals

#### Public (Limited Read)

- Read active packages only
- View basic package information
- No write/delete access
- Portal/website visibility

### Record Rules

- **Multi-Company Rule**: Users can only access packages in their companies
- **Domain**: `[('company_id', 'in', company_ids)]`
- Applies to Staff and Managers

---

## Technical Details

### Model: `cater.package`

- **Table**: `cater_package`
- **Inherits**: `mail.thread`, `mail.activity.mixin`
- **Order**: `sequence, name`

### Dependencies

- `cater.menu.item`: Menu items must exist
- `cater.service`: Services must exist
- `res.company`: Multi-company support
- `res.currency`: Multi-currency support

### Computed Fields

All computed fields are stored for performance:

- `menu_total`: Sum of menu line subtotals
- `service_total`: Sum of service line subtotals
- `estimated_cost`: Based on pricing method
- `is_available`: Based on current date and availability dates
- `booking_count`: Count of related bookings

---

## Troubleshooting

### Package Not Appearing in Booking Dropdown

**Possible Causes**:

- Package is archived (active=False)
- Package belongs to different company
- User lacks read access

**Solution**:

- Check package active status
- Verify company assignment matches booking
- Check user access rights

### Prices Not Auto-Filling in Booking

**Cause**: This is expected behavior

**Explanation**:

- Booking line prices come from menu items/services, not package
- Package stores reference prices for estimation
- Booking gets current prices from items

**Solution**: No action needed, working as designed

### Package Items Not Populating

**Possible Causes**:

- JavaScript error in browser
- Onchange method not triggered
- Menu items/services deleted

**Solution**:

- Clear browser cache
- Check browser console for errors
- Verify all package items still exist
- Restart Odoo service

### Cannot Delete Package

**Cause**: Package is referenced by bookings

**Solution**:

- Archive package instead of deleting
- Or remove package reference from all bookings first
- Use "Archive" action from Action menu

---

## Future Enhancements (Roadmap)

### Planned Features

- [ ] Package recommendations based on guest count
- [ ] Package availability calendar view
- [ ] Package comparison tool
- [ ] Dynamic pricing based on booking date
- [ ] Package add-ons and upgrades
- [ ] Package templates/categories
- [ ] Package analytics dashboard
- [ ] Package rating/feedback system
- [ ] Package discount rules
- [ ] Package versioning

### API Endpoints (Planned)

- REST API for package catalog
- Website/portal package selection
- Third-party integration support

---

## Support & Documentation

### Related Documentation

- See main `README.md` for full module documentation
- Check `models/package.py` for technical implementation
- Review `views/package_views.xml` for UI customization

### Getting Help

1. Check this documentation first
2. Review Odoo logs for errors
3. Test in development environment
4. Contact system administrator

---

## Summary

The Catering Packages feature streamlines the event booking process by allowing pre-configured bundles of menu items and services. With three flexible pricing models, visual kanban cards, and seamless booking integration, packages make it easy to offer standardized options while maintaining the flexibility to customize each booking.

Key advantages:

- ⚡ **Speed**: Create bookings faster with one-click package selection
- 🎯 **Consistency**: Ensure the same quality and offerings every time
- 💰 **Pricing Flexibility**: Support multiple pricing models
- 📊 **Tracking**: Monitor which packages are most popular
- 🎨 **Visual**: Use images for better marketing
- 🏢 **Multi-Company**: Full support for multiple companies

Start creating packages today to streamline your catering operations!

---

**Last Updated**: November 16, 2025  
**Version**: 2.0  
**Module**: Catering Management (`cater`)
