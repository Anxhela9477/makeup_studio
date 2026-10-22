{
    'name': 'Makeup Studio',
    'version': '1.0',
    'summary': 'Makeup Studio',
    'description': 'Makeup Studio',
    'category': 'Services',
    'author': 'Author',

    'depends': ['base'],

    'data': [
       'security/security.xml',
       'security/ir.model.access.csv',
       'wizard/appointment_report_wizard_view.xml',
        'reports/appointment_report.xml',
        'views/client_view.xml',
        'views/service_view.xml',
        'views/appointment_view.xml',
        'views/payment_view.xml',
        'views/holiday_request_view.xml',
        'views/discount_view.xml',
        'views/inventory_view.xml',
        'views/menu.xml',
        
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}