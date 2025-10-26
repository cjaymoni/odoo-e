{
    'name': 'ExpressPay Ghana',
    'version': '1.0',
    'summary': 'Payment Provider: ExpressPay Ghana with hybrid webhook system',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'depends': [   
        'base',
        'website',
        'payment',
        'website_sale',
        'account'],
    'data': [
        'views/payment_expresspay_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',  # To pre-configure ExpressPay in DB
    ],
    'installable': True,
    'application': False,

    'license': 'LGPL-3',
    'icon': '/expresspay_ghana/static/description/icon3.jpg',
    'images': [
        'static/description/icon1.png',
        'static/description/icon3.jpg',
    ],

}