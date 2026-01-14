from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    # Ejemplo de lógica extra
    real_worked_hours = fields.Float(
        string='Horas Reales',
        compute='_compute_real_worked_hours',
        store=True
    )

    @api.depends('check_in', 'check_out')
    def _compute_real_worked_hours(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                delta = rec.check_out - rec.check_in
                rec.real_worked_hours = delta.total_seconds() / 3600
            else:
                rec.real_worked_hours = 0.0