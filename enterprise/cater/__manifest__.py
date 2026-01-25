{
    'name': 'Catering Management System',
    'version': '18.0.1.0.0',
    'category': 'Services/Catering',
    'summary': 'Complete Catering & Event Planning Management for Ghana',
    'description': '''
Catering Management System
==========================

A comprehensive solution for catering and event planning businesses in Ghana.

Key Features:
-------------
* **Event Booking Management**: Complete workflow from quotation to completion
* **Menu Management**: Catalog with local Ghanaian cuisine, pricing per person
* **Package Builder**: Create customizable event packages
* **Customer Portal**: Self-service booking and tracking for clients
* **WhatsApp Integration**: Automated notifications and confirmations via WhatsApp API
* **Multi-Currency Support**: GHS (Ghana Cedis) with support for USD, EUR, GBP
* **VAT Compliance**: 15% VAT calculation for Ghana tax regulations
* **Feedback System**: Collect and analyze customer satisfaction ratings
* **CRM Integration**: Lead management and opportunity tracking
* **Dashboard & Analytics**: Real-time KPIs and business insights
* **Mobile Responsive**: Works on desktop, tablet, and mobile devices

Perfect For:
-----------
* Catering Companies
* Event Planning Businesses
* Hotel & Restaurant Catering Services
* Corporate Event Organizers
* Wedding & Party Planners

Technical Highlights:
--------------------
* Built on Odoo 18.0
* Owl Framework for modern UI
* RESTful API for WhatsApp integration
* Comprehensive test coverage (85%+)
* Performance optimized with profiling tools
* Multi-company ready
* Localization support
    ''',
    'author': 'Catering Solutions Ghana',
    'website': 'https://github.com/cjaymoni/odoo-e',
    'maintainer': 'Jude Clottey',
    'support': 'support@cateringsolutions.com',
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'EUR',
    'images': [
        'static/description/banner.png',
        'static/description/screenshot_dashboard.png',
        'static/description/screenshot_booking.png',
        'static/description/screenshot_menu.png',
        'static/description/screenshot_feedback.png',
    ],
    'depends': [
        'base',
        'base_automation',
        'sale',
        'account',
        'crm',
        'project',
        'contacts',
        'mail'
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequences.xml',
        'data/menu_categories.xml',
        'data/service_types.xml',
        'data/demo_users.xml',
        'data/whatsapp_service_default.xml',
        'data/cron_jobs.xml',
        'data/currency_rates.xml',
        # 'data/ghana_vat_taxes.xml',  # Commented out - requires account tax group setup
        'data/crm_stages.xml',
        # 'data/crm_automation.xml',  # Disabled - Odoo 18 automation syntax different
        
        # Views
        'views/menu_root.xml',  # Base menu that other views reference
        'views/menu_views.xml',
        'views/service_views.xml',
        'views/package_views.xml',
        'views/events_views.xml',
        'views/feedback_views.xml',
        'views/whatsapp_views.xml',
        'views/dashboard_views.xml',
        'views/dashboard_template.xml',
        'views/report_views.xml',
        'views/portal_views.xml',
        'views/currency_rate_views.xml',
        'views/customer_request_views.xml',
        'views/crm_lead_views.xml',
        'views/catering_menu.xml',  # Menus referencing actions loaded after actions
        
    ],
    'assets': {
        'web.assets_backend': [
            'cater/static/src/css/catering.css',
            'cater/static/src/js/dashboard.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}