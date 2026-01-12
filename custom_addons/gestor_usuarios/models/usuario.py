from odoo import models, fields, api

class Usuario(models.Model):
    # id de la tabla
    _name = 'gestor_usuarios.usuario'
    _description = 'Esto es un modelo de usuario del gestor'

    # Aqui declaramos las varibles (char,float,integer)
    name = fields.Char(string='Nombre', required=True)
    lastname = fields.Char(string='Apellido', required=True)
    age = fields.Integer(string='Edad', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Telefono', required=True)

    # Campos computados
    cantidad = fields.Float(string='Cantidad')

    precio = fields.Float(string='$')

    # Con store en true si se almacena en la BD
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    # # Tienes que especificar de quien depende el calculo,  con el @api.depends
    # Los campos computados no se almacenan
    @api.depends('cantidad', 'precio')
    def _compute_total(self):
        for record in self:
            record.total = (record.cantidad or 0) * (record.precio or 0)

    # api.onChange se lanza cuando debo disparar una acción
    @api.onchange('age')
    def _onchange_age(self):
        if self.age and self.age < 18:
            return {
                'warning': {
                    'title': 'Advertencia',
                    'message': 'El usuario es menor de edad.'
                }
            }
