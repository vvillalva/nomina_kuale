{
    'name': 'Gestor de Usuarios',
    'version': '1.0',
    'description': "Gestor de usuarios para administrativos",
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',

        'views/employees_view.xml',
        'views/usuarios_view.xml',

        'views/menu_items.xml',
    ],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
}