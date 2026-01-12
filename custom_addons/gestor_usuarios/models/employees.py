from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date(string='Fecha de nacimiento')


    # como ya existe el modelo no hacemos reglas de seguridad