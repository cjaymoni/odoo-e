# Catering Management System for Odoo 18

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-purple.svg)](https://www.odoo.com/)
[![Build Status](https://github.com/cjaymoni/odoo-e/workflows/CI/badge.svg)](https://github.com/cjaymoni/odoo-e/actions)

A comprehensive catering and event planning management system specifically designed for the Ghanaian market, built on Odoo 18.

## 🎯 Features

### Event Booking Management

- **Complete Booking Workflow**: Draft → Confirmed → In Progress → Completed
- **Event Types**: Weddings, Corporate Events, Birthdays, Graduations, and more
- **Guest Management**: Track guest count and special requirements
- **Venue Management**: Store venue details and preferences
- **State-based Workflow**: Clear status tracking throughout the event lifecycle

### Menu & Package Management

- **Menu Catalog**: Comprehensive menu items with categories
- **Ghanaian Cuisine Focus**: Local dishes like Jollof Rice, Banku, Fufu, and more
- **Per-Person Pricing**: Flexible pricing based on guest count
- **Minimum Order Quantities**: Enforce minimum orders per menu item
- **Package Builder**: Create and manage event packages with predefined menu and services

### Financial Management

- **Multi-Currency Support**: Primary GHS with USD, EUR, GBP support
- **Real-time Exchange Rates**: Automatic currency conversion
- **VAT Compliance**: 15% VAT calculation for Ghana tax regulations
- **Automatic Calculations**: Subtotal, tax, and total amount computed automatically
- **Invoicing Integration**: Seamless integration with Odoo Accounting

### WhatsApp Integration

- **Automated Notifications**: Booking confirmations, reminders, and updates
- **Template Messages**: Pre-configured WhatsApp message templates
- **Webhook Support**: Handle WhatsApp API responses
- **Status Tracking**: Monitor message delivery status
- **Media Support**: Send images and documents via WhatsApp

### Customer Management

- **CRM Integration**: Lead and opportunity management
- **Customer Portal**: Self-service booking and tracking
- **Contact Management**: Store customer details, preferences, and history
- **Booking History**: View all past and upcoming events per customer
- **Feedback Collection**: Customer satisfaction ratings and reviews

### Analytics & Reporting

- **Real-time Dashboard**: KPIs for bookings, revenue, and customer satisfaction
- **Performance Metrics**: Track monthly growth and trends
- **Feedback Analytics**: Detailed ratings for food quality, service, presentation, and timeliness
- **Upcoming Events**: View all scheduled events for the next 7 days
- **Recent Activity**: Timeline of important booking updates

### Additional Features

- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Multi-Company**: Support for multiple catering businesses
- **Portal Access**: Client portal for self-service booking management
- **Automated Workflows**: Cron jobs for reminders and follow-ups
- **Comprehensive Testing**: 85%+ test coverage with automated CI/CD
- **Performance Optimized**: Includes profiling tools for monitoring

## 📸 Screenshots

![Dashboard](static/description/screenshot_dashboard.png)
_Real-time dashboard with KPIs and analytics_

![Booking Management](static/description/screenshot_booking.png)
_Comprehensive booking form with menu and service selection_

![Menu Catalog](static/description/screenshot_menu.png)
_Menu management with categories and pricing_

![Customer Feedback](static/description/screenshot_feedback.png)
_Feedback collection and analysis system_

## 🚀 Installation

### Requirements

- Odoo 18.0 or higher
- Python 3.10+
- PostgreSQL 13+
- Dependencies: base, base_automation, sale, account, crm, project, contacts, mail

### Standard Installation

1. **Download the module**

   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/cjaymoni/odoo-e.git
   cd odoo-e/enterprise/cater
   ```

2. **Update apps list**

   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Catering Management System"

3. **Install the module**
   - Click Install button
   - Wait for installation to complete

### Docker Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/cjaymoni/odoo-e.git
   cd odoo-e
   ```

2. **Start services**

   ```bash
   docker-compose up -d
   ```

3. **Access Odoo**
   - Open http://localhost:8069
   - Create database
   - Install "Catering Management System" module

### Odoo.sh Deployment

1. **Connect your GitHub repository**

   - Link your Odoo.sh project to the GitHub repository
   - Select the branch (odoo-18-catering-app)

2. **Configure settings**

   - Set environment variables for WhatsApp API
   - Configure email server settings
   - Set up domain and SSL certificates

3. **Deploy**
   - Odoo.sh will automatically deploy
   - Install the module from Apps menu

## ⚙️ Configuration

### Initial Setup

1. **Configure Company Settings**

   - Go to Settings → General Settings → Companies
   - Set currency to GHS (Ghana Cedis)
   - Configure VAT (15% for Ghana)

2. **Set Up User Groups**

   ```
   - Catering Client: Portal access for customers
   - Catering Staff: Basic booking management
   - Catering Manager: Full access to configuration
   ```

3. **Configure WhatsApp Integration** (Optional)

   - Go to Catering → Configuration → WhatsApp Settings
   - Enter WhatsApp Business API credentials:
     - Phone Number ID
     - Access Token
     - Webhook Verify Token
     - Business Account ID
   - Test connection

4. **Create Menu Categories**

   - Go to Catering → Configuration → Menu Categories
   - Add categories (e.g., Main Dishes, Sides, Beverages, Desserts)

5. **Add Menu Items**

   - Go to Catering → Menu Items
   - Create menu items with:
     - Name and description
     - Category
     - Price per person
     - Minimum order quantity

6. **Configure Services**
   - Go to Catering → Configuration → Services
   - Add services like:
     - Staff (waiters, bartenders)
     - Equipment (tables, chairs, sound system)
     - Transportation
     - Decoration

## 📖 User Guide

### For Customers (Portal Users)

1. **Create Booking Request**

   - Access the customer portal
   - Click "Request Quote"
   - Fill in event details
   - Submit request

2. **Track Bookings**

   - View all bookings in portal
   - Check status updates
   - Receive WhatsApp notifications

3. **Provide Feedback**
   - After event completion
   - Rate food quality, service, presentation, timeliness
   - Add comments and recommendations

### For Staff

1. **Manage Bookings**

   - View all bookings in Kanban/List view
   - Update booking status
   - Add menu items and services
   - Generate quotations

2. **Customer Communication**
   - Send WhatsApp notifications
   - Update customers on booking status
   - Handle special requests

### For Managers

1. **Dashboard Overview**

   - Monitor KPIs (bookings, revenue, satisfaction)
   - View upcoming events
   - Track recent activity

2. **Configuration**

   - Manage menu items and pricing
   - Configure services and packages
   - Set up automation rules
   - Manage user access

3. **Reports & Analytics**
   - Generate financial reports
   - Analyze customer feedback
   - Track performance metrics

## 🧪 Testing

The module includes comprehensive test coverage (85%+):

```bash
# Run all tests
./run_tests.sh

# Run specific test categories
docker-compose exec odoo python3 odoo-bin \
    -c /etc/odoo/odoo.conf \
    -d test_db \
    -u cater \
    --test-enable \
    --test-tags=workflow \
    --stop-after-init

# Generate coverage report
docker-compose exec odoo pip install coverage
docker-compose exec odoo coverage run --source=enterprise/cater \
    python3 odoo-bin -c /etc/odoo/odoo.conf \
    -d test_db -u cater --test-enable --stop-after-init
docker-compose exec odoo coverage report
```

## 🔧 Development

### Project Structure

```
cater/
├── __init__.py
├── __manifest__.py
├── controllers/          # HTTP controllers for webhooks
├── data/                 # Demo data and configurations
├── models/              # Business logic models
├── security/            # Access rights and record rules
├── static/
│   ├── description/     # Module screenshots and banner
│   ├── src/
│   │   ├── css/        # Stylesheets
│   │   └── js/         # Owl components
│   └── icon.png        # Module icon
├── tests/              # Unit and integration tests
├── tools/              # Profiling and utilities
├── views/              # XML views and templates
└── i18n/               # Translation files
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `./run_tests.sh`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use ES6+ for JavaScript
- Add docstrings to all public methods
- Write tests for new features
- Maintain 85%+ code coverage

## 🐛 Known Issues

- WhatsApp API requires valid Business API credentials
- Currency rates need manual update if internet connection is unavailable
- Dashboard requires at least one booking to display KPIs

## 🗺️ Roadmap

### Version 2.0 (Q2 2026)

- [ ] Mobile app for staff (Android/iOS)
- [ ] Online payment integration (Paystack, Flutterwave)
- [ ] Advanced inventory management
- [ ] Recipe management with cost tracking
- [ ] Staff scheduling and time tracking

### Version 3.0 (Q4 2026)

- [ ] AI-powered menu recommendations
- [ ] Predictive analytics for demand forecasting
- [ ] Multi-language support (Twi, Ga, Ewe)
- [ ] Advanced reporting dashboard
- [ ] API marketplace integration

## 📄 License

This module is licensed under LGPL-3. See [LICENSE](LICENSE) file for details.

## 💬 Support

- **Documentation**: [GitHub Wiki](https://github.com/cjaymoni/odoo-e/wiki)
- **Issues**: [GitHub Issues](https://github.com/cjaymoni/odoo-e/issues)
- **Email**: support@cateringsolutions.com
- **Community**: [Odoo Community Forum](https://www.odoo.com/forum)

## 👥 Credits

### Authors

- Jude Clottey (@cjaymoni)

### Contributors

- [List of contributors](https://github.com/cjaymoni/odoo-e/contributors)

### Maintainer

This module is maintained by Catering Solutions Ghana.

## 🙏 Acknowledgments

- Odoo Community Association (OCA) for best practices
- Ghana Revenue Authority for VAT guidelines
- WhatsApp Business API documentation
- Open-source community for continuous support

---

**Made with ❤️ in Ghana 🇬🇭**
