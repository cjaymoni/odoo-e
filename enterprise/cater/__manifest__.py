{
    'name': 'Catering Management 2.0',
    'version': '18.0.1.0.0',
    'category': 'Services',
    'summary': 'Ghanaian Catering & Event Planning Management System',
    'description': '''
        Complete catering and event management solution for Ghana:
        - Event booking and planning
        - Menu management with local cuisine
        - Customer relationship management
        - WhatsApp integration for notifications
        - Local pricing in GHS with multi-currency support
        - VAT compliance for Ghana
        - Feedback collection and analytics
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
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
        'data/ghana_vat_taxes.xml',
        'data/crm_stages.xml',
        # 'data/crm_automation.xml',  # Disabled - Odoo 18 automation syntax different
        
        # Views
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
        'views/catering_menu.xml',
        
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
}