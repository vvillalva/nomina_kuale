from odoo import models, fields

class NominaAdjustmentLine(models.Model):
    _name = 'nomina_kuale.adjustment.line'
    _description = 'Ajuste de Pago'

    nomina_id = fields.Many2one(
        'nomina_kuale.employee',
        string="Nómina",
        ondelete="cascade",
        required=True
    )

    adjustment_type = fields.Selection(
        [
            ('abono', 'Abono'),
            ('salario', 'Salario'),
            ('cargo', 'Cargo'),
        ],
        string="Tipo",
        required=True
    )

    concept = fields.Char(
        string="Concepto de Ajuste",
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='nomina_id.currency_id',
        store=True
    )

    amount = fields.Monetary(
        string="Monto",
        currency_field='currency_id',
        required=True
    )

    description = fields.Char(
        string="Descripción"
    )