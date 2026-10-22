from odoo import models, fields, api


class MakeupStudioUser(models.Model):
    _name = 'makeup_studio.user'
    _description = 'Makeup Studio User'
    _rec_name = 'user_code'

    user_code = fields.Char(
        string='User ID',
        readonly=True,
        copy=False
    )

    name = fields.Char(
        string='Name',
        required=True
    )

    email = fields.Char(
        string='Email',
        required=True
    )

    password = fields.Char(
        string='Password'
    )

    phone = fields.Char(
        string='Phone'
    )

    role = fields.Selection([
        ('client', 'Client'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
    ], string='Role', required=True, default='client')

    loyalty_points = fields.Integer(
        string='Loyalty Points',
        default=0
    )

    registered_date = fields.Date(
        string='Registered Date',
        default=fields.Date.today
    )
    work_monday = fields.Boolean(string='Monday')
    work_tuesday = fields.Boolean(string='Tuesday')
    work_wednesday = fields.Boolean(string='Wednesday')
    work_thursday = fields.Boolean(string='Thursday')
    work_friday = fields.Boolean(string='Friday')
    work_saturday = fields.Boolean(string='Saturday')
    work_sunday = fields.Boolean(string='Sunday')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    total_worked_hours = fields.Float(string='Total Worked Hours')
    salary = fields.Float(string='Salary')
    hire_date = fields.Date(string='Hire Date')

    staff_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('day_off', 'Day Off'),
    ], string='Staff Status', default='active')

    @api.model
    def create(self, vals):
        role = vals.get('role', 'client')

        if role == 'client':
            prefix = 'CL'
        elif role == 'staff':
            prefix = 'ST'
        elif role == 'manager':
            prefix = 'MG'
        else:
            prefix = 'US'

        record = super().create(vals)

        record.user_code = f"{prefix}{record.id:04d}"

        return record
