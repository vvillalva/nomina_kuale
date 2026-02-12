{
    'name': 'Adminisitrador de Usuarios',
    'category': 'Productivity',
    'description': "Gestor de tareas asignadas por usuario. - Practica Odoo",
    'summary': 'Modulo para gestiorar tareas asignadas por usuario.',
    'version': '1.0',
    'author': 'Victor Villalva',
    'depends': ['base'],
    'data': [
        'security/task_security.xml',
        'security/ir.model.access.csv',
        'views/task_views.xml'
    ],
    'assets':{},
    'installable': True,
    'application': True,
    'auto_install': False,
}