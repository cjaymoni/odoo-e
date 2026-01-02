# 👥 User Roles and Permissions - Catering Management

## Overview

The Catering Management module implements a comprehensive role-based access control (RBAC) system with four distinct user roles, each designed for specific operational needs:

1. **Event Planner** - Core operational role for booking management
2. **Accountant** - Financial operations and reporting
3. **Staff** - Extended operational access (inherits Event Planner)
4. **Admin** - Full system access (inherits Staff and Accountant)
5. **Client (Portal)** - Read-only customer portal access

---

## 🎯 Role Hierarchy

```
┌─────────────────────────────────────────┐
│              Admin                      │
│  (Full Access to Everything)            │
│  Inherits: Staff + Accountant           │
└─────────────┬───────────────────────────┘
              │
       ┌──────┴──────┐
       │             │
┌──────▼─────┐ ┌────▼──────────┐
│   Staff    │ │  Accountant   │
│  Enhanced  │ │  Financial    │
│Operations  │ │  Operations   │
│            │ │               │
│ Inherits:  │ │ Implied:      │
│ Event      │ │ Account       │
│ Planner    │ │ Invoice Group │
└──────┬─────┘ └───────────────┘
       │
┌──────▼─────────────────┐
│   Event Planner        │
│  Core Bookings         │
│  Packages & Services   │
└────────────────────────┘

┌────────────────────────┐
│  Client (Portal)       │
│  Read-Only Access      │
│  Own Records Only      │
└────────────────────────┘
```

---

## 1️⃣ Event Planner Role

### Purpose

Core operational role focused on event booking creation and coordination with clients.

### Access Level

**Read & Write** (Limited Create/Delete permissions)

### Responsibilities

- Create and manage event bookings
- Select packages for events
- Coordinate menu items and services
- Communicate with clients
- Update booking status
- View feedback

### Permissions

#### Can Do:

✅ **Bookings**

- Create new event bookings
- Edit existing bookings
- View all bookings in their company
- Change booking status
- Add/edit menu lines and service lines
- Cannot delete bookings

✅ **Packages**

- View all packages
- Select packages for bookings
- Cannot create/edit/delete packages

✅ **Services**

- View all services
- Add services to bookings
- Cannot create/edit/delete services

✅ **Menu Items**

- View all menu items
- Add menu items to bookings
- Cannot create/edit/delete menu items

✅ **Feedback**

- View customer feedback
- Create feedback entries
- Edit feedback
- Cannot delete feedback

#### Cannot Do:

❌ Delete bookings
❌ Create/edit packages
❌ Create/edit services
❌ Create/edit menu items
❌ Access financial reports
❌ Configure WhatsApp integration
❌ Manage system configuration

### Menu Access

```
Catering Management
├── Event Planning ✅
│   ├── Bookings
│   │   ├── Events ✅
│   │   └── Today's Events ✅
│   ├── Packages ✅ (View Only)
│   └── Services ✅ (View Only)
├── Accounting ❌
├── Menu Management ❌
├── Feedback & Analytics ❌
├── Reports ❌
└── WhatsApp ❌
```

---

## 2️⃣ Accountant Role

### Purpose

Financial operations, payment tracking, and accounting integration.

### Access Level

**Read & Write** (Limited to financial aspects)

### Responsibilities

- View all bookings for financial tracking
- Update payment information
- Process invoices
- Generate financial reports
- Track deposits and balances
- Reconcile payments

### Permissions

#### Can Do:

✅ **Bookings (Financial View)**

- View all bookings
- Edit payment fields (deposit, paid amount, balance due)
- View financial totals
- Cannot create new bookings
- Cannot delete bookings

✅ **Financial Data**

- View menu line prices
- View service line prices
- View booking totals
- Access accounting integration

✅ **Reports**

- Generate financial reports
- Export financial data

#### Cannot Do:

❌ Create bookings
❌ Delete bookings
❌ Edit menu/service lines
❌ Access event planning features
❌ Configure packages or services
❌ Access WhatsApp integration

### Menu Access

```
Catering Management
├── Event Planning ❌
├── Accounting ✅
│   └── Booking Financials ✅
├── Menu Management ❌
├── Feedback & Analytics ❌
├── Reports ✅ (Financial Only)
└── WhatsApp ❌
```

### Integration

- Implied access to: `account.group_account_invoice`
- Can access Odoo Accounting module
- Can create and manage invoices
- Can reconcile payments

---

## 3️⃣ Staff Role

### Purpose

Extended operational access combining Event Planner capabilities with additional management features.

### Access Level

**Read, Write, Create** (No delete on critical records)

### Responsibilities

- All Event Planner responsibilities
- Create and manage menu items
- Create and manage services
- Manage packages
- View analytics and dashboards
- Generate reports
- Manage customer feedback

### Permissions

#### Inherits All Event Planner Permissions Plus:

✅ **Menu Management**

- Create menu items
- Edit menu items
- Create menu categories
- Edit menu categories
- Cannot delete menu items/categories

✅ **Service Management**

- Create services
- Edit services
- Cannot delete services

✅ **Package Management**

- Create packages
- Edit packages
- Duplicate packages
- Cannot delete packages

✅ **Analytics**

- View dashboard
- Access analytics
- View reports

✅ **Feedback**

- View all feedback
- Edit feedback (read-only, cannot create for customers)

#### Cannot Do:

❌ Delete critical records (bookings, packages, services, menu items)
❌ Configure WhatsApp integration
❌ Manage system settings
❌ Full financial operations (use Accountant for this)

### Menu Access

```
Catering Management
├── Event Planning ✅
│   ├── Bookings ✅
│   │   ├── Events ✅
│   │   └── Today's Events ✅
│   ├── Packages ✅ (Full Access)
│   └── Services ✅ (Full Access)
├── Accounting ❌
├── Menu Management ✅
│   ├── Menu Items ✅
│   └── Categories ✅
├── Feedback & Analytics ✅
│   ├── Customer Feedback ✅
│   └── Dashboard ✅
├── Reports ✅
│   └── Generate Reports ✅
└── WhatsApp ❌
```

---

## 4️⃣ Admin Role

### Purpose

Complete system administration with full access to all features and configuration.

### Access Level

**Full Access** (Read, Write, Create, Delete)

### Responsibilities

- All Staff responsibilities
- All Accountant responsibilities
- System configuration
- WhatsApp integration setup
- User management
- Security settings
- Full deletion rights

### Permissions

#### Has Everything:

✅ **Complete Event Planner Access**
✅ **Complete Staff Access**
✅ **Complete Accountant Access**

#### Plus Exclusive Access:

✅ **System Configuration**

- Manage all system settings
- Configure integrations
- Manage sequences

✅ **WhatsApp Integration**

- Configure WhatsApp service
- View message logs
- Manage automation

✅ **User Management**

- Assign user roles
- Manage permissions
- Create/delete users

✅ **Full Delete Rights**

- Delete bookings (with caution)
- Delete packages
- Delete services
- Delete menu items
- Archive/unarchive records

✅ **Multi-Company**

- Access all companies
- Manage company settings

### Menu Access

```
Catering Management (Full Access to All)
├── Event Planning ✅
│   ├── Bookings ✅
│   │   ├── Events ✅
│   │   └── Today's Events ✅
│   ├── Packages ✅
│   └── Services ✅
├── Accounting ✅
│   └── Booking Financials ✅
├── Menu Management ✅
│   ├── Menu Items ✅
│   └── Categories ✅
├── Feedback & Analytics ✅
│   ├── Customer Feedback ✅
│   └── Dashboard ✅
├── Reports ✅
│   └── Generate Reports ✅
└── WhatsApp ✅
    ├── Configuration ✅
    └── Message Logs ✅
```

---

## 5️⃣ Client (Portal) Role

### Purpose

Read-only customer portal access for clients to view their own bookings.

### Access Level

**Read & Limited Write** (Own records only)

### Responsibilities

- View their own bookings
- Provide feedback
- Update basic booking details
- View menu items and services in their bookings

### Permissions

#### Can Do:

✅ **Own Bookings Only**

- View bookings where they are the customer
- Edit basic booking details (venue, guest count, etc.)
- Create new bookings for themselves
- Cannot delete bookings

✅ **Own Feedback**

- View their feedback
- Create feedback for their bookings
- Edit their feedback
- Cannot delete feedback

✅ **Menu & Services**

- View menu items (read-only)
- View services (read-only)
- View packages (read-only)
- View their booking lines

✅ **Sales Orders**

- View their own sales orders
- View order lines
- Track payment status

#### Cannot Do:

❌ View other customers' bookings
❌ Delete any records
❌ Access backend management features
❌ View analytics or reports
❌ Configure anything

### Data Isolation

**Security Rules Applied:**

```python
# Bookings Rule
domain: [('partner_id.user_ids', 'in', [user.id])]

# Feedback Rule
domain: [('booking_id.partner_id.user_ids', 'in', [user.id])]

# Sales Orders Rule
domain: [('partner_id.user_ids', 'in', [user.id])]
```

This ensures clients can ONLY see records where they are the linked customer.

### Portal Access

- Access via: `https://your-domain.com/my/bookings`
- Login with portal credentials
- Clean, customer-friendly interface
- Mobile-responsive design

---

## 🔐 Security Implementation

### Record Rules

All roles have company-based data isolation:

```xml
<!-- Multi-Company Rule -->
<record id="catering_booking_company_rule" model="ir.rule">
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

This ensures users only see records from their assigned companies.

### Access Rights Matrix

| Model               | Admin | Staff | Event Planner | Accountant     | Client   |
| ------------------- | ----- | ----- | ------------- | -------------- | -------- |
| **Bookings**        |
| Read                | ✅    | ✅    | ✅            | ✅             | ✅ (Own) |
| Write               | ✅    | ✅    | ✅            | ✅ (Financial) | ✅ (Own) |
| Create              | ✅    | ✅    | ✅            | ❌             | ✅ (Own) |
| Delete              | ✅    | ❌    | ❌            | ❌             | ❌       |
| **Packages**        |
| Read                | ✅    | ✅    | ✅            | ❌             | ✅       |
| Write               | ✅    | ✅    | ❌            | ❌             | ❌       |
| Create              | ✅    | ✅    | ❌            | ❌             | ❌       |
| Delete              | ✅    | ❌    | ❌            | ❌             | ❌       |
| **Services**        |
| Read                | ✅    | ✅    | ✅            | ❌             | ✅       |
| Write               | ✅    | ✅    | ❌            | ❌             | ❌       |
| Create              | ✅    | ✅    | ❌            | ❌             | ❌       |
| Delete              | ✅    | ❌    | ❌            | ❌             | ❌       |
| **Menu Items**      |
| Read                | ✅    | ✅    | ✅            | ❌             | ✅       |
| Write               | ✅    | ✅    | ❌            | ❌             | ❌       |
| Create              | ✅    | ✅    | ❌            | ❌             | ❌       |
| Delete              | ✅    | ❌    | ❌            | ❌             | ❌       |
| **Feedback**        |
| Read                | ✅    | ✅    | ✅            | ❌             | ✅ (Own) |
| Write               | ✅    | ❌    | ✅            | ❌             | ✅ (Own) |
| Create              | ✅    | ❌    | ✅            | ❌             | ✅ (Own) |
| Delete              | ✅    | ❌    | ❌            | ❌             | ❌       |
| **WhatsApp Config** |
| Read                | ✅    | ❌    | ❌            | ❌             | ❌       |
| Write               | ✅    | ❌    | ❌            | ❌             | ❌       |
| Create              | ✅    | ❌    | ❌            | ❌             | ❌       |
| Delete              | ✅    | ❌    | ❌            | ❌             | ❌       |

---

## 📋 Assigning Roles to Users

### Via Settings > Users & Companies > Users

1. **Open User Record**

   - Go to Settings → Users & Companies → Users
   - Select the user or create a new one

2. **Assign Catering Role**

   - Scroll to "Access Rights" tab
   - Find "Catering Management" section
   - Select appropriate role:
     - **Event Planner** - For booking coordinators
     - **Accountant** - For financial staff
     - **Staff** - For operations managers
     - **Admin** - For system administrators
     - **Client (Portal)** - For customer portal users

3. **Save Changes**

### Role Selection Guidelines

**Choose Event Planner when:**

- User only needs to create and manage bookings
- User coordinates with clients
- User doesn't need to create packages or services
- Focus is on day-to-day event operations

**Choose Accountant when:**

- User handles payments and invoices
- User needs financial reporting
- User shouldn't create bookings
- Focus is on financial tracking

**Choose Staff when:**

- User needs to create packages and services
- User manages menu items
- User needs analytics access
- User requires more than basic booking operations

**Choose Admin when:**

- User manages the entire system
- User configures integrations
- User needs full access including deletions
- System administrator or owner

**Choose Client (Portal) when:**

- External customer needs access
- Customer should only see their own data
- Read-only portal access required
- Customer feedback collection needed

---

## 🎬 Common Role-Based Workflows

### Event Planner Daily Workflow

1. **Morning**: Check "Today's Events"
2. **Review**: View all bookings for the day
3. **Create**: New booking from customer inquiry
4. **Select**: Package to auto-fill items
5. **Customize**: Adjust menu/services as needed
6. **Confirm**: Change booking status to confirmed
7. **Track**: Update booking progress throughout day
8. **Follow-up**: Check feedback after event

### Accountant Daily Workflow

1. **Morning**: Review "Booking Financials"
2. **Check**: All bookings with pending payments
3. **Update**: Record deposit payments received
4. **Process**: Create invoices for confirmed bookings
5. **Reconcile**: Match payments with invoices
6. **Generate**: Financial reports for management
7. **Follow-up**: Contact customers with outstanding balances

### Staff Weekly Workflow

1. **Monday**: Review dashboard and analytics
2. **Update**: Menu items based on seasonal availability
3. **Create**: New packages for upcoming season
4. **Maintain**: Update service pricing
5. **Review**: Customer feedback from past week
6. **Generate**: Reports for management review
7. **Coordinate**: With Event Planners on special requests

### Admin Monthly Workflow

1. **Review**: All system activity and usage
2. **Manage**: User access and permissions
3. **Configure**: WhatsApp automation settings
4. **Analyze**: Business performance metrics
5. **Update**: System configuration as needed
6. **Backup**: Verify data backups
7. **Plan**: Future system enhancements

---

## 🔧 Technical Implementation

### Security Groups Definition

Located in: `security/security.xml`

```xml
<!-- Event Planner Group -->
<record id="catering_event_planner_group" model="res.groups">
    <field name="name">Event Planner</field>
    <field name="category_id" ref="module_category_catering"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- Accountant Group -->
<record id="catering_accountant_group" model="res.groups">
    <field name="name">Accountant</field>
    <field name="implied_ids" eval="[(4, ref('base.group_user')),
                                     (4, ref('account.group_account_invoice'))]"/>
</record>

<!-- Staff Group (inherits Event Planner) -->
<record id="catering_staff_group" model="res.groups">
    <field name="name">Staff</field>
    <field name="implied_ids" eval="[(4, ref('catering_event_planner_group'))]"/>
</record>

<!-- Admin Group (inherits Staff + Accountant) -->
<record id="catering_manager_group" model="res.groups">
    <field name="name">Admin</field>
    <field name="implied_ids" eval="[(4, ref('catering_staff_group')),
                                     (4, ref('catering_accountant_group'))]"/>
</record>

<!-- Client Portal Group -->
<record id="catering_client_group" model="res.groups">
    <field name="name">Client (Portal)</field>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Access Rights Definition

Located in: `security/ir.model.access.csv`

Format: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`

Example:

```csv
access_event_booking_event_planner,cater.event.booking.event_planner,model_cater_event_booking,catering_event_planner_group,1,1,1,0
access_event_booking_accountant,cater.event.booking.accountant,model_cater_event_booking,catering_accountant_group,1,1,0,0
```

### Menu Access Control

Located in: `views/catering_menu.xml`

```xml
<!-- Event Planner Access -->
<menuitem id="catering_event_planner_menu"
          name="Event Planning"
          groups="catering_event_planner_group,catering_staff_group,catering_manager_group"/>

<!-- Accountant Access -->
<menuitem id="catering_accounting_menu"
          name="Accounting"
          groups="catering_accountant_group,catering_manager_group"/>

<!-- Admin Only -->
<menuitem id="catering_whatsapp_menu"
          name="WhatsApp"
          groups="catering_manager_group"/>
```

---

## 📚 Best Practices

### For Administrators

1. **Least Privilege Principle**

   - Assign minimum necessary role for each user
   - Start with Event Planner, upgrade only if needed
   - Regularly review user access

2. **Role Assignment**

   - Document why each user has their role
   - Review permissions quarterly
   - Remove access when users leave

3. **Security Auditing**
   - Monitor admin activities
   - Review deletion logs
   - Track permission changes

### For Event Planners

1. **Daily Operations**

   - Focus on booking creation and management
   - Request Staff access if you need package creation
   - Escalate financial issues to Accountant

2. **Data Entry**
   - Always select packages when available
   - Fill in all required fields
   - Add notes for special requirements

### For Accountants

1. **Financial Tracking**

   - Update payment status daily
   - Generate invoices promptly
   - Reconcile weekly

2. **Communication**
   - Coordinate with Event Planners on payment issues
   - Report financial metrics to Admin
   - Flag unusual payment patterns

### For Staff

1. **Content Management**

   - Keep menu items updated
   - Create seasonal packages
   - Maintain service catalog

2. **Analytics**
   - Review dashboard weekly
   - Generate reports for planning
   - Share insights with team

---

## 🆘 Troubleshooting

### "Access Denied" Errors

**Problem**: User sees "Access Denied" when trying to access a feature

**Solutions**:

1. Verify user has correct role assigned
2. Check if company assignment matches
3. Confirm user session is current (logout/login)
4. Review record rules aren't blocking access

### User Can't See Certain Records

**Problem**: User can't see bookings/packages they should see

**Solutions**:

1. Check multi-company settings
2. Verify user company matches record company
3. Review record rule domains
4. Check if records are archived

### Client Sees Other Customers' Data

**Problem**: Portal client can see records they shouldn't

**Solutions**:

1. Verify Client (Portal) group is assigned (not Staff)
2. Check partner_id is correctly linked
3. Review record rules are active
4. Check user isn't in multiple groups

---

## 📖 Related Documentation

- Main README: `README.md`
- Package Management: `PACKAGES.md`
- Security Configuration: `security/security.xml`
- Access Rights: `security/ir.model.access.csv`

---

**Last Updated**: November 16, 2025  
**Version**: 2.0  
**Module**: Catering Management (`cater`)
