from odoo import models, fields, api

class Employee(models.Model):
    _name = 'nomina_kuale.employee'
    _description = 'Registro de Pagos de Empleados'

#   DATOS DE MODELO DE EMPLEADO
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True,
    )

    company_employee = fields.Many2one(
        related='employee_id.company_id',
        string='Empresa del empleado',
    )

    department_employee_id = fields.Many2one(
        related='employee_id.department_id',
        string='Departamento del Trabajador',
    )

    job_employee_id = fields.Many2one(
        related='employee_id.job_id',
        string='Puesto del Trabajador',
    )

    rol_employee_id = fields.Many2one(
        related='employee_id.rol_tab_id',
        string='Rol del Trabajador',
    )

    curp_employee_id = fields.Char(
        related='employee_id.curp',
        string='Curp del Trabajador',
    )

    rfc_employee_id = fields.Char(
        related='employee_id.rfc_number',
        string='RFC del Trabajador',
    )
#   DATOS BANCARIOS DEL EMPLEADO
    bank_account_employee_id = fields.Many2one(
        'bank.account',
        string='Cuenta Bancaria',
        compute='_compute_bank_account_employee',
        store=True,
        readonly=True
    )

    account_type = fields.Char(
        related='bank_account_employee_id.account_type',
        string='Tipo de cuenta',
    )

    bank_name = fields.Char(
        related='bank_account_employee_id.bank',
        string='Nombre del Banco',
    )

    account_number = fields.Char(
        related='bank_account_employee_id.account_number',
        string='Cuenta de Banco',
    )

    interbank_clabe = fields.Char(
        related='bank_account_employee_id.interbank_clabe',
        string='Cuenta Interbancaria',
    )

    payroll_card_number = fields.Char(
        related='bank_account_employee_id.payroll_card_number',
        string='Numero de Tajeta de Nomina',
    )
    applicant_id = fields.Many2one(
        'hr.applicant',
        store=True,
        readonly=True,
    )
# DATOS DEL CONTRATO
    contract_id = fields.Many2one(
        'hr.contract',
        string='Contrato del Empleado',
        compute='_compute_contract_id',
        store=True,
        readonly=True,
    )

    date_start = fields.Date(
        related='contract_id.date_start',
        string='Fecha de Inicio de Contrato'
    )

    structure_type_id = fields.Many2one(
        related='contract_id.structure_type_id',
        string='Estructura Salarial'
    )

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )

    wage = fields.Monetary(
        related='contract_id.wage',
        string='Salario del Contrato'
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    adjustment_line_ids = fields.One2many(
        'nomina_kuale.adjustment.line',
        'nomina_id',
        string="Ajustes de Pago"
    )

    total_adjustment = fields.Float(
        compute='_compute_total_adjustment',
        store=True,
        string='Total Ajustes'
    )

    total_payment = fields.Monetary(
        compute='_compute_total_payment',
        store=True,
        string='Total a pagar'
    )

    @api.depends('employee_id', 'employee_id.bank_account_ids')
    def _compute_bank_account_employee(self):
        for rec in self:
            rec.bank_account_employee_id = False

            if not rec.employee_id:
                continue

            accounts = rec.employee_id.bank_account_ids.sorted('id')

            if accounts:
                rec.bank_account_employee_id = accounts[0]

    @api.depends('employee_id')
    def _compute_contract_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.contract_id:
                rec.contract_id = rec.employee_id.contract_id
            else:
                rec.contract_id = False

    @api.depends('adjustment_line_ids.amount', 'adjustment_line_ids.adjustment_type')
    def _compute_total_adjustment(self):
        for rec in self:
            total = 0.0
            for line in rec.adjustment_line_ids:
                if line.adjustment_type == 'abono':
                    total += line.amount
                elif line.adjustment_type == 'cargo':
                    total -= line.amount

            rec.total_adjustment = total

    @api.depends('wage', 'total_adjustment')
    def _compute_total_payment(self):
        for rec in self:
            rec.total_payment = (rec.wage or 0.0) + (rec.total_adjustment or 0.0)