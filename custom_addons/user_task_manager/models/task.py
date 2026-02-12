from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class UserTask(models.Model):
    _name = 'user.task'
    _description = 'User Task'
    _order = 'deadline asc'

    name = fields.Char(string='Nombre de Tarea', required=True, help='Ingresa el nombre del tarea')
    description = fields.Text(string='Descripción',  help='Ingresa una descripción para la tarea')
    priority = fields.Selection(
        [('0','Baja'), ('1','Media'),('2','Alta')],
        string='Prioridad',
        default='1',
        required=True,
    )
    state = fields.Selection(
        [('draft','Borrador'),('in_progress','En Progreso'), ('done','Completado')],
        string='Estado',
        default='draft',
    )
    deadline = fields.Date(string='Fecha limite', help='Ingresa la fecha de la tarea')
    is_done = fields.Boolean(string='Estado', compute='_compute_is_done', store=True, default=False)
    user_id = fields.Many2one(
        'res.users',
        string='Asignado a',
        default=lambda self: self.env.user, #Relacionamos con el usuario autenticado
        required=True,
    )
    #Campo Computado - Se ejecuta automaticamente cuando cambie el estado
    @api.depends('state')
    def _compute_is_done(self):
        for record in self:
            record.is_done = record.state == 'done'

    # Valida que la fecha limite no sea anterior a la actual
    @api.constrains('deadline')
    def _check_deadline(self):
        for task in self:
            if task.deadline and task.deadline < fields.Date.today():
                raise ValidationError('La fecha limite no puede ser anterior a hoy.')
