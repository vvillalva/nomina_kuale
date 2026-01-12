{
    'name': 'Nomina Kuale',
    'description': "Nomina Kuale - Odoo 17",
    'version': '1.0',
    'website': 'www.dwit.mx',
    'author': 'DWIT',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'reclutamiento__kuale',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/employee_view.xml',

        'views/menu_items.xml',
    ],
    'assets':{},
    'installable': True,
    'application': True,
    'auto_install': False,
}