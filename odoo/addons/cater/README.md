# Catering Management 2.0

A comprehensive catering and event planning management system designed specifically for the Ghanaian market, built for Odoo 18.0.

![Version](https://img.shields.io/badge/version-18.0.1.0.0-blue)
![License](https://img.shields.io/badge/license-LGPL--3-green)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Security](#security)
- [Testing](#testing)
- [Support](#support)

## 🎯 Overview

Catering Management 2.0 is a complete end-to-end solution for catering businesses in Ghana, providing:

- **Event booking and planning** with comprehensive workflow management
- **Menu management** with local Ghanaian cuisine support
- **Customer relationship management** with automated communications
- **WhatsApp integration** for notifications and feedback collection
- **Financial tracking** with Ghana VAT compliance (15%)
- **Analytics dashboard** with real-time KPIs and charts
- **Customer portal** for self-service booking management
- **Advanced reporting** with multiple export formats
- **Multi-company support** for managing multiple catering businesses

## ✨ Features

### 🎉 Event Management

- **Multiple event types**: Wedding, Birthday, Corporate, Funeral, Outdooring, Graduation
- **Complete workflow**: Draft → Confirmed → In Progress → Completed → Cancelled
- **Venue conflict detection** to prevent double bookings
- **Guest count management** (1-1,000 guests)
- **Event duration tracking** (up to 24 hours)
- **Special requests** and dietary restrictions
- **Automatic reminders** via WhatsApp

### 🍽️ Menu Management

- **Categorized menu items** with images
- **Price per person** in GHS (Ghanaian Cedis)
- **Minimum order quantities**
- **Preparation time tracking**
- **Dietary flags**: Vegetarian, Spicy
- **Allergen information**
- **Availability windows**

### 💰 Financial Management

- **Multi-currency support** (default: GHS)
- **Automatic VAT calculation** (15% Ghana standard)
- **Deposit requirements** (50% default)
- **Payment tracking** with balance calculations
- **Sales order integration**
- **Invoice generation**
- **Financial reporting** and analytics

### 📱 WhatsApp Integration (Twilio)

- **Automated notifications**:
  - Booking confirmations
  - Event reminders (1 day before)
  - Feedback requests (after completion)
  - Feedback confirmations
- **Delivery status tracking**
- **Incoming message handling**
- **Message logging** with complete audit trail
- **Opt-in/opt-out management**
- **Development mode** for testing without signature validation

### ⭐ Customer Feedback System

- **5-star rating system** (Poor to Excellent)
- **Detailed ratings** for:
  - Food quality (1-5)
  - Service quality (1-5)
  - Presentation (1-5)
  - Timeliness (1-5)
- **Overall score calculation**
- **Recommendation tracking**
- **Multiple feedback sources**: WhatsApp, Phone, Email, In-Person
- **One feedback per booking** constraint
- **Automated collection** via scheduled jobs

### 📊 Analytics & Dashboard

- **Key Performance Indicators**:
  - Total bookings with growth percentage
  - Revenue tracking with growth trends
  - Average customer satisfaction
  - Completed events count
  - Active customers
  - Pending bookings
- **Visual charts**:
  - Booking trends over time
  - Revenue trends
  - Event type distribution
  - Rating distribution
  - Monthly performance comparison
- **Real-time updates** with intelligent caching
- **Recent activity feed**
- **Upcoming events overview**

### 📈 Advanced Reporting

- **Report types**:
  - Customer Feedback Summary
  - Satisfaction Trends Analysis
  - Booking Analysis
  - Financial Summary
  - Performance Metrics
- **Export formats**: PDF, Excel, CSV
- **Flexible filters**:
  - Date ranges
  - Customer selection
  - Event type filtering
  - Custom parameters

### 🌐 Customer Portal

- **Self-service booking management**
- **View all bookings** with search and filters
- **Submit feedback** after events
- **Browse menu items**
- **Track booking status**
- **Pagination** for large datasets

## 📦 Installation

### Prerequisites

- Odoo 18.0 or higher
- Python 3.10+
- PostgreSQL 12+

### Required Odoo Modules

- `base`
- `sale`
- `account`
- `crm`
- `project`
- `contacts`
- `mail`

### Optional Python Libraries

For WhatsApp signature validation:

```bash
pip install twilio
```

For advanced features:

```bash
pip install requests
```

### Installation Steps

1. **Copy the module** to your Odoo addons directory:

   ```bash
   cp -r cater /path/to/odoo/addons/
   ```

2. **Update the addons list**:

   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Catering Management 2.0"

3. **Install the module**:

   - Click Install button
   - Wait for installation to complete

4. **Configure permissions**:
   - Assign users to appropriate groups:
     - **Catering Manager**: Full access
     - **Catering Staff**: Operational access
     - **Catering Client**: Customer access

## ⚙️ Configuration

### 1. WhatsApp Setup (Twilio)

1. **Get Twilio credentials**:

   - Sign up at [twilio.com](https://www.twilio.com)
   - Get Account SID and Auth Token
   - Set up WhatsApp Business number

2. **Configure in Odoo**:

   - Go to **Catering → Configuration → WhatsApp Service**
   - Create/Edit WhatsApp service record
   - Enter:
     - Account SID
     - Auth Token
     - From Number (WhatsApp Business number)
     - Optional: Messaging Service SID
   - Test connection using "Test Connection" button

3. **Set base URL** for webhooks:

   - Go to **Settings → Technical → System Parameters**
   - Set `web.base.url` to your public domain (e.g., `https://yourdomain.com`)
   - Configure Twilio webhook URL: `https://yourdomain.com/whatsapp/webhook`

4. **Development mode** (optional):
   - Create system parameter: `cater.whatsapp.dev_mode` = `True`
   - This skips signature validation for local testing

### 2. Currency Setup

The module defaults to GHS (Ghanaian Cedis). To configure:

1. Go to **Settings → Accounting → Currencies**
2. Activate GHS if not already active
3. Set exchange rates if using multiple currencies

### 3. Multi-Company Setup

The module fully supports multi-company environments. Each company can have:

- **Separate menu items and categories**
- **Company-specific services**
- **Independent bookings and customer data**
- **Dedicated WhatsApp configuration**
- **Company-filtered analytics and reports**

**To configure multiple companies:**

1. **Enable multi-company mode**:

   - Go to **Settings → Users & Companies → Companies**
   - Create additional companies as needed

2. **Assign users to companies**:

   - Go to **Settings → Users & Companies → Users**
   - Edit each user
   - Set **Allowed Companies** and **Default Company**

3. **Configure per-company data**:

   - Switch to each company using the company selector in top right
   - Set up menu items, services, and WhatsApp configuration
   - Create bookings specific to that company

4. **Access control**:
   - Users can only see data from their allowed companies
   - Dashboard and reports automatically filter by current company
   - Record rules ensure data isolation

**Benefits:**

- ✅ Manage multiple catering brands from one installation
- ✅ Separate pricing and menus per location/brand
- ✅ Independent WhatsApp configurations
- ✅ Consolidated reporting across companies (for admin users)
- ✅ Data privacy and security between companies

### 4. Menu Categories & Items

1. **Load demo data** (optional):

   - Menu categories are pre-loaded during installation
   - Service types are pre-configured

2. **Create custom items**:
   - Go to **Catering → Menu → Menu Items**
   - Create items with pricing and details
   - Upload images for better presentation

### 4. Scheduled Actions

Two cron jobs are pre-configured:

- **Event Reminders**: Runs daily, sends reminders 1 day before events
- **Feedback Collection**: Runs every 6 hours, sends feedback requests

To modify:

- Go to **Settings → Technical → Automation → Scheduled Actions**
- Search for "Catering"
- Adjust intervals as needed

### 5. User Groups

Assign users to groups:

1. Go to **Settings → Users & Companies → Users**
2. Edit user
3. Go to **Access Rights** tab
4. Select appropriate Catering Management group:
   - **Manager**: Full access (admin only)
   - **Staff**: Day-to-day operations
   - **Client**: Portal customers (optional)

## 🚀 Usage

### Creating a Booking

1. Go to **Catering → Bookings → Event Bookings**
2. Click **Create**
3. Fill in event details:
   - Customer information
   - Event name and type
   - Date, time, and venue
   - Expected guest count
4. Add menu items:
   - Click "Add a line" in Menu Items tab
   - Select items and quantities
5. Add services (optional):
   - Equipment rental
   - Additional staff
   - Decorations, etc.
6. Review totals (automatically calculated with 15% VAT)
7. Click **Confirm** to:
   - Lock the booking
   - Create sales order
   - Send WhatsApp confirmation

### Managing Events

- **Start Event**: Click "Start Event" button when service begins
- **Complete Event**: Click "Complete" when finished
  - Automatically triggers feedback request
- **Cancel**: Click "Cancel" if event is cancelled

### Collecting Feedback

**Automatic** (recommended):

- System sends WhatsApp feedback request after completion
- Customer responds via WhatsApp link or portal

**Manual**:

- Go to **Catering → Feedback → Customer Feedback**
- Create new feedback record
- Link to completed booking
- Enter ratings and comments

### Viewing Analytics

1. Go to **Catering → Dashboard**
2. View real-time KPIs and charts
3. Filter by date ranges
4. Export data or generate reports

### Generating Reports

1. Go to **Catering → Reporting → Generate Report**
2. Select report type
3. Set date range and filters
4. Choose export format (PDF/Excel/CSV)
5. Click **Generate Report**

## 🔧 Technical Details

### Architecture

```
cater/
├── models/              # Business logic
│   ├── menu_item.py            # Menu management
│   ├── event_booking.py        # Core booking logic
│   ├── catering_service.py     # Additional services
│   ├── feedback.py             # Feedback system
│   ├── whatsapp_integration.py # WhatsApp/Twilio
│   ├── dashboard.py            # Analytics engine
│   ├── reports.py              # Report generation
│   ├── res_partner_extend.py   # Customer extensions
│   └── account_move_extend.py  # Invoice links
├── controllers/         # HTTP endpoints
│   ├── portal.py               # Customer portal
│   └── whatsapp_webhook.py     # Twilio webhooks
├── views/              # UI definitions
├── data/               # Default data & cron jobs
├── security/           # Access control
├── static/             # CSS, JS, images
└── tests/              # Unit tests
```

### Data Models

**Core models** (13 total):

- `cater.menu.category` - Menu categorization
- `cater.menu.item` - Individual menu items
- `cater.service` - Additional services
- `cater.event.booking` - Main booking records
- `cater.booking.menu.line` - Menu items per booking
- `cater.booking.service.line` - Services per booking
- `cater.feedback` - Customer feedback
- `cater.whatsapp.service` - WhatsApp configuration
- `cater.whatsapp.log` - Message audit trail
- `cater.dashboard` - Dashboard data model
- `cater.report.wizard` - Report wizard
- Extensions to `res.partner` and `account.move`

### Performance Optimizations

- **Database indexes** on frequently queried fields:
  - Event dates
  - Booking states
  - Partner-state combinations
  - Feedback ratings
  - Company IDs (for multi-company filtering)
- **ORM caching** for dashboard data (user-level)
- **Computed fields** with `store=True` for efficiency
- **Batch operations** support in create/write methods
- **Smart cache invalidation** on data changes
- **check_company_auto** enabled on all models for automatic company validation

### Multi-Company Architecture

- **Company field** on all core models (bookings, menus, services, feedback, logs)
- **Automatic company propagation** through related records (booking → feedback, etc.)
- **Record rules** enforce company-level data isolation
- **Dashboard filtering** by current company context
- **Check company** validation on all Many2one relationships
- **Company indexes** for optimized queries

### API Endpoints

- `POST /whatsapp/webhook` - Twilio callback handler
  - Handles incoming messages
  - Processes delivery status updates
  - Optional signature validation

## 🔒 Security

### User Groups (3-tier)

1. **Catering Manager**

   - Full access to all features
   - Configuration management
   - Delete permissions
   - Reporting and analytics

2. **Catering Staff**

   - Operational access
   - Create/edit bookings
   - View all records
   - No delete permissions
   - No WhatsApp configuration access

3. **Catering Client**
   - Portal access only
   - View own bookings
   - Submit feedback
   - Browse menu items
   - No backend access

### Record-Level Security

- **Row-level security (RLS)** for client group
- Clients can only access their own bookings and feedback
- Staff can modify confirmed bookings (managers only)
- Comprehensive access rules (37+ rules in CSV)
- **Multi-company record rules** automatically filter data by company
- **Company-based access control** for all models
- Users can only access data from their allowed companies

### Data Validation

**31+ validation constraints** including:

- ✅ Prices must be positive
- ✅ Event dates must be in future (except completed)
- ✅ No venue conflicts (same venue/date/time)
- ✅ Guest count limits (1-1,000)
- ✅ Payment validation (non-negative, within total)
- ✅ Duration limits (0-24 hours)
- ✅ One feedback per booking
- ✅ Feedback only for completed events
- ✅ Rating ranges (1-5)

## 🧪 Testing

### Test Suite

Run tests with:

```bash
odoo-bin -c odoo.conf -u cater --test-enable --stop-after-init
```

### Test Coverage

- **Model tests** (`test_catering_models.py`)
  - Booking creation and workflow
  - Calculation accuracy (totals, VAT, deposits)
  - Validation constraints
- **Security tests** (`test_security.py`)

  - Access control rules
  - Row-level security
  - Permission enforcement

- **Integration tests** (`test_whatsapp_integration.py`)

  - WhatsApp message sending
  - Status tracking
  - Error handling

- **Controller tests** (`test_webhook_controllers.py`)
  - Webhook processing
  - Signature validation
  - Incoming message handling

### Manual Testing Checklist

- [ ] Create booking with menu items and services
- [ ] Verify VAT calculation (15%)
- [ ] Confirm booking and check sales order creation
- [ ] Test WhatsApp notifications
- [ ] Complete event and verify feedback request
- [ ] Submit feedback via portal
- [ ] Generate reports in different formats
- [ ] Test venue conflict detection
- [ ] Verify client portal access restrictions
- [ ] Check dashboard data accuracy

## 📊 Database Schema

### Key Tables

```sql
-- Event bookings
cater_event_booking (indexed on: event_date, state, partner_id)

-- Menu items
cater_menu_item, cater_menu_category

-- Feedback with constraints
cater_feedback (indexed on: rating, create_date)
  UNIQUE(booking_id)
  CHECK(rating BETWEEN 1 AND 5)

-- WhatsApp integration
cater_whatsapp_service, cater_whatsapp_log
```

## 🐛 Troubleshooting

### WhatsApp Not Sending

1. Check WhatsApp service is active
2. Verify Twilio credentials
3. Ensure customer has `whatsapp_opt_in = True`
4. Check phone number format (E.164: +233...)
5. Review logs in Catering → Configuration → WhatsApp Logs

### Dashboard Not Loading

1. Clear cache: Delete dashboard cache records
2. Check user permissions
3. Review server logs for errors
4. Verify database indexes exist

### Booking Totals Incorrect

1. Check VAT rate (should be 15%)
2. Verify menu item prices
3. Check service line quantities
4. Review compute methods in logs

### Portal Access Issues

1. Verify user is in `catering_client_group`
2. Check portal access is enabled
3. Ensure booking belongs to user's partner
4. Review record rules in Settings → Technical

## 📝 Best Practices

### For Managers

- Review dashboard daily for KPIs
- Monitor feedback and respond to low ratings
- Keep menu items and prices updated
- Regularly export reports for analysis
- Maintain WhatsApp opt-in list

### For Staff

- Always add menu items before confirming
- Double-check venue and date for conflicts
- Enter special requests accurately
- Confirm bookings promptly
- Mark events as completed same day

### For Developers

- Use proper field types (Monetary for money)
- Add validation constraints liberally
- Index frequently queried fields
- Cache expensive computations
- Write tests for new features
- Follow Odoo coding standards

## 🔄 Upgrade Notes

### From 1.x to 2.0

- Backup database before upgrading
- Review new WhatsApp configuration
- Update user group assignments
- Test webhook endpoints
- Regenerate reports to use new format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Follow Odoo code conventions
5. Submit pull request with clear description

## 📄 License

This module is licensed under LGPL-3.

## 📞 Support

For issues, questions, or feature requests:

- **Email**: support@yourcompany.com
- **Website**: https://www.yourcompany.com
- **Documentation**: https://docs.yourcompany.com/catering

## 🙏 Acknowledgments

- Built for the Ghanaian catering industry
- Twilio for WhatsApp Business API
- Odoo SA for the amazing framework
- All contributors and testers

## 📈 Roadmap

### Completed Features ✅

- [x] **Multi-company support** - Full support for managing multiple companies
  - Company-specific bookings, menus, and services
  - Separate WhatsApp configurations per company
  - Company-filtered dashboards and analytics
  - Record-level security rules

### Planned Features

- [ ] Email integration for notifications
- [ ] Online payment gateway (Paystack, Flutterwave)
- [ ] Calendar view for bookings
- [ ] Resource scheduling (staff, equipment)
- [ ] Inventory management for ingredients
- [ ] Mobile app (iOS/Android)
- [ ] AI-powered menu recommendations
- [ ] Automated pricing optimization
- [ ] Integration with accounting software

---

**Version**: 18.0.1.0.0  
**Last Updated**: November 2025  
**Status**: Production Ready ✅
