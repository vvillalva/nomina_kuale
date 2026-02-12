{
    'name': 'STP Servicios - Kuale',
    'category': 'Productivity',
    'description': """
    Módulo para la gestión de servicios STP:
    - Registro de órdenes de pago
    - Generación de claves de rastreo
    - Envío y consulta de operaciones STP
    - Integración con servicios bancarios
    - Control de estatus de pagos
        """,
    'summary': 'Integración y gestión de servicios STP (Sistema de Transferencias y Pagos)',
    'version': '1.0',
    'author': 'DWIT',
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