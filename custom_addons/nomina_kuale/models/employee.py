from odoo import models, fields, api
from datetime import date, datetime, time, timedelta
from calendar import monthrange

class Employee(models.Model):
    _name = 'nomina_kuale.employee'
    _description = 'Registro de Pagos de Empleados'

#   DATOS DE MODELO DE EMPLEADO
    name = fields.Char(
        string='Nombre',
        required=True
    )

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
    #Aqui consumo el modelo de adjustmenNomina.py
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

    # DIAS TRABAJADOS
    attendance_ids = fields.One2many(
        related='employee_id.attendance_ids',
        string='Asistencias',
        readonly=True
    )

#   QUINCENAS / NÓMINA POR DÍAS
    quincena_name = fields.Selection(
        [('q1', '1ra Quincena'), ('q2', '2ra Quincena')],
        string='Quincena Actual',
        compute='_compute_quincena_data',
        store=False,
    )

    quincena_date_start = fields.Date(
        string='Inicio de Quincena',
        compute='_compute_quincena_data',
        store=False,
    )

    quincena_date_end = fields.Date(
        string='Fin quincena',
        compute='_compute_quincena_data',
        store=False
    )

    pay_per_day = fields.Monetary(
        string='Pago por dia',
        compute='_compute_pay_per_day',
        store=False,
        currency_field='currency_id',
    )

    attended_days_quincena = fields.Integer(
        string='Días asistidos (quincena)',
        compute='_compute_attended_days_quincena',
        store=False,
    )

    quincenal_payment_total = fields.Monetary(
        string='Pago quincenal total',
        compute='_compute_quincenal_payment_total',
        store=False,
        currency_field='currency_id',
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

    def _get_today_date(self):
        """Fecha de hoy respetando el timezone/contexto del usuario."""
        return fields.Date.context_today(self)

    @api.depends()
    def _compute_quincena_data(self):
        for rec in self:
            today = rec._get_today_date()
            if not today:
                rec.quincena_name = False
                rec.quincena_date_start = False
                rec.quincena_date_end = False
                continue

            last_day = monthrange(today.year, today.month)[1]
            month_start = date(today.year, today.month, 1)
            month_end = date(today.year, today.month, last_day)

            if today.day <= 15:
                rec.quincena_name = 'q1'
                rec.quincena_date_start = month_start
                rec.quincena_date_end = date(today.year, today.month, 15)
            else:
                rec.quincena_name = 'q2'
                rec.quincena_date_start = date(today.year, today.month, 16)
                rec.quincena_date_end = month_end

    @api.depends('wage')
    def _compute_pay_per_day(self):
        for rec in self:
            wage = rec.wage or 0.0
            rec.pay_per_day = wage / 30.0 if wage else 0.0

    def _generate_absence_adjustment(self):
        Adjustment = self.env['nomina_kuale.adjustment.line']

        for rec in self:
            if not rec.employee_id or not rec.quincena_date_start or not rec.quincena_date_end:
                continue

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', datetime.combine(rec.quincena_date_start, time.min)),
                ('check_in', '<=', datetime.combine(rec.quincena_date_end, time.max)),
            ])

            attended_days = set()
            for att in attendances:
                local_dt = fields.Datetime.context_timestamp(rec, att.check_in)
                attended_days.add(local_dt.date())

            current_day = rec.quincena_date_start
            while current_day <= rec.quincena_date_end:
                # 0 = lunes, 4 = viernes
                if current_day.weekday() < 5:
                    if current_day not in attended_days:
                        exists = Adjustment.search([
                            ('nomina_id', '=', rec.id),
                            ('adjustment_type', '=', 'cargo'),
                            ('concept', '=', 'COBRO POR FALTA'),
                            ('description', 'ilike', current_day.strftime('%d/%m/%Y')),
                        ], limit=1)

                        if not exists:
                            Adjustment.create({
                                'nomina_id': rec.id,
                                'adjustment_type': 'cargo',
                                'concept': 'COBRO POR FALTA',
                                'amount': rec.pay_per_day,
                                'description': f'El empleado faltó el día {current_day.strftime("%d/%m/%Y")}',
                            })
                current_day += timedelta(days=1)

    def _generate_attendance_adjustments(self):
        Adjustment = self.env['nomina_kuale.adjustment.line']

        for rec in self:
            if not rec.employee_id or not rec.quincena_date_start or not rec.quincena_date_end:
                continue

            # 1️⃣ Asistencias de la quincena
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', datetime.combine(rec.quincena_date_start, time.min)),
                ('check_in', '<=', datetime.combine(rec.quincena_date_end, time.max)),
            ])

            attended_days = set()
            for att in attendances:
                local_dt = fields.Datetime.context_timestamp(rec, att.check_in)
                attended_days.add(local_dt.date())

            # 2️⃣ Generar abono por cada día asistido (lunes a viernes)
            for day in attended_days:
                if day.weekday() < 5:  # lunes a viernes

                    exists = Adjustment.search([
                        ('nomina_id', '=', rec.id),
                        ('adjustment_type', '=', 'abono'),
                        ('concept', '=', 'DIA DE ASISTENCIA'),
                        ('description', 'ilike', day.strftime('%d/%m/%Y')),
                    ], limit=1)

                    if not exists:
                        Adjustment.create({
                            'nomina_id': rec.id,
                            'adjustment_type': 'abono',
                            'concept': 'DIA DE ASISTENCIA',
                            'amount': rec.pay_per_day,
                            'description': f'Pago del día de asistencia del empleado ({day.strftime("%d/%m/%Y")})',
                        })

    @api.depends('attendance_ids.check_in', 'employee_id', 'quincena_date_start', 'quincena_date_end')
    def _compute_attended_days_quincena(self):
        for rec in self:
            rec.attended_days_quincena = 0

            if not rec.employee_id or not rec.quincena_date_start or not rec.quincena_date_end:
                continue

            # Traemos asistencias del empleado en el rango de la quincena
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', datetime.combine(rec.quincena_date_start, time.min)),
                ('check_in', '<=', datetime.combine(rec.quincena_date_end, time.max)),
            ])

            # Convertimos check_in a fecha (día) y hacemos set para contar días únicos
            attended_dates = set()
            for att in attendances:
                check_in_local = fields.Datetime.context_timestamp(rec, att.check_in)
                attended_dates.add(check_in_local.date())

            rec.attended_days_quincena = len(attended_dates)
            # CARGOS POR FALTAS
            rec._generate_absence_adjustment()
            # ABONOS POR ASISTENCIA
            rec._generate_attendance_adjustments()

    @api.depends('attended_days_quincena', 'pay_per_day')
    def _compute_quincenal_payment_total(self):
        for rec in self:
            rec.quincenal_payment_total = (rec.attended_days_quincena or 0) * (rec.pay_per_day or 0.0)


