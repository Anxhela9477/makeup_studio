from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class MakeupAppointment(models.Model):
    _name = 'makeup_studio.appointment'
    _description = 'Makeup Studio Appointment'
    _rec_name = 'appointment_code'



    appointment_code = fields.Char(
        string='Appointment ID',
        readonly=True,
        copy=False
    )

    client_id = fields.Many2one(
        'makeup_studio.user',
        string='Client',
        domain=[('role', '=', 'client')],
        required=True
    )

    service_id = fields.Many2one(
        'makeup_studio.service',
        string='Service',
        required=True
    )

    price = fields.Float(
        string='Service Price',
        related='service_id.price',
        store=True,
        readonly=True
    )

    staff_id = fields.Many2one(
        'makeup_studio.user',
        string='Makeup Artist / Staff',
        domain=[
            ('role', 'in', ['staff', 'manager']),
            ('staff_status', '=', 'active')
        ],
        required=True
    )

    appointment_datetime = fields.Datetime(
        string='Appointment Date & Time',
        required=True
    )

    notes = fields.Text(
        string='Notes'
    )

    # ---------------------------------------------------------
    # LOYALTY / DISCOUNT
    # ---------------------------------------------------------

    available_loyalty_points = fields.Integer(
        string='Available Loyalty Points',
        related='client_id.loyalty_points',
        readonly=True
    )

    discount_id = fields.Many2one(
        'makeup_studio.discount',
        string='Discount',
        domain=[('active', '=', True)]
    )

    loyalty_points_used = fields.Integer(
        string='Loyalty Points Used',
        default=0
    )

    discount_amount = fields.Float(
        string='Discount Amount',
        compute='_compute_prices',
        store=True
    )

    final_price = fields.Float(
        string='Final Price',
        compute='_compute_prices',
        store=True
    )


    status = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ],
        string='Status',
        default='pending',
        required=True
    )


    @api.model
    def create(self, vals):
        record = super().create(vals)

        record.appointment_code = f"APP{record.id:04d}"

        return record

    @api.depends(
        'price',
        'loyalty_points_used',
        'discount_id',
        'discount_id.discount_amount'
    )
    def _compute_prices(self):
        for record in self:

            # 10 loyalty points = €1
            loyalty_discount = (
                record.loyalty_points_used / 10.0
            )

            rule_discount = 0.0

            if record.discount_id:
                rule_discount = (
                    record.discount_id.discount_amount
                )

            total_discount = (
                loyalty_discount + rule_discount
            )

            # Discount cannot exceed service price
            total_discount = min(
                total_discount,
                record.price
            )

            record.discount_amount = total_discount

            record.final_price = max(
                record.price - total_discount,
                0.0
            )


    @api.constrains(
        'loyalty_points_used',
        'client_id',
        'price',
        'discount_id'
    )
    def _check_loyalty_points(self):
        for record in self:

            if record.loyalty_points_used < 0:
                raise ValidationError(
                    'Loyalty points used cannot be negative.'
                )

            if (
                record.client_id
                and record.loyalty_points_used
                > record.client_id.loyalty_points
            ):
                raise ValidationError(
                    'The client does not have enough loyalty points.'
                )

            if (
                record.loyalty_points_used / 10.0
                > record.price
            ):
                raise ValidationError(
                    'The loyalty discount cannot be greater '
                    'than the service price.'
                )
            if (
                record.discount_id
                and record.client_id
                and record.client_id.loyalty_points
                < record.discount_id.minimum_points
            ):
                raise ValidationError(
                    f'This discount requires at least '
                    f'{record.discount_id.minimum_points} '
                    f'loyalty points.'
                )

            # Combined discount cannot exceed service price
            if record.discount_id:

                loyalty_discount = (
                    record.loyalty_points_used / 10.0
                )

                total_discount = (
                    loyalty_discount
                    + record.discount_id.discount_amount
                )

                if total_discount > record.price:
                    raise ValidationError(
                        'The total discount cannot be greater '
                        'than the service price.'
                    )

    def action_approve(self):
        for record in self:
            record.status = 'approved'

    def action_complete(self):
        for record in self:

            record.status = 'completed'

            payments = self.env[
                'makeup_studio.payment'
            ].search([
                ('appointment_id', '=', record.id),
                ('payment_status', '=', 'paid')
            ])

            payments._process_loyalty_points()

    def action_cancel(self):
        for record in self:
            record.status = 'cancelled'


    @api.constrains(
        'staff_id',
        'appointment_datetime'
    )
    def _check_staff_holiday(self):
        for record in self:

            if (
                not record.staff_id
                or not record.appointment_datetime
            ):
                continue

            local_datetime = (
                fields.Datetime.context_timestamp(
                    record,
                    record.appointment_datetime
                )
            )

            appointment_date = local_datetime.date()

            holiday = self.env[
                'makeup_studio.holiday_request'
            ].search([
                ('staff_id', '=', record.staff_id.id),
                ('status', '=', 'approved'),
                ('start_date', '<=', appointment_date),
                ('end_date', '>=', appointment_date)
            ], limit=1)

            if holiday:
                raise ValidationError(
                    f'{record.staff_id.name} is on approved '
                    f'holiday on this date.'
                )


    @api.constrains(
        'staff_id',
        'appointment_datetime'
    )
    def _check_staff_working_schedule(self):
        for record in self:

            if (
                not record.staff_id
                or not record.appointment_datetime
            ):
                continue

            staff = record.staff_id

            # Staff must be active
            if staff.staff_status != 'active':
                raise ValidationError(
                    f'{staff.name} is not currently active.'
                )

            local_datetime = (
                fields.Datetime.context_timestamp(
                    record,
                    record.appointment_datetime
                )
            )

            weekday = local_datetime.weekday()

            working_days = {
                0: staff.work_monday,
                1: staff.work_tuesday,
                2: staff.work_wednesday,
                3: staff.work_thursday,
                4: staff.work_friday,
                5: staff.work_saturday,
                6: staff.work_sunday,
            }

            if not working_days.get(weekday):
                raise ValidationError(
                    f'{staff.name} does not work on '
                    f'{local_datetime.strftime("%A")}.'
                )

            appointment_time = (
                local_datetime.hour
                + local_datetime.minute / 60.0
            )

            if staff.start_time < staff.end_time:

                if not (
                    staff.start_time
                    <= appointment_time
                    < staff.end_time
                ):
                    raise ValidationError(
                        f'{staff.name} is not working '
                        f'at the selected time.'
                    )

    # ---------------------------------------------------------
    # CHECK APPOINTMENT OVERLAP
    # ---------------------------------------------------------

    @api.constrains(
        'staff_id',
        'appointment_datetime',
        'service_id',
        'status'
    )
    def _check_staff_appointment_overlap(self):
        for record in self:

            if (
                not record.staff_id
                or not record.appointment_datetime
                or not record.service_id
            ):
                continue

            # Cancelled appointment does not block time
            if record.status == 'cancelled':
                continue

            new_start = record.appointment_datetime

            duration_hours = (
                record.service_id.duration or 0.0
            )

            new_end = new_start + timedelta(
                hours=duration_hours
            )

            # Only appointments for SAME STAFF
            other_appointments = self.search([
                ('id', '!=', record.id),
                ('staff_id', '=', record.staff_id.id),
                ('status', '!=', 'cancelled')
            ])

            for other in other_appointments:

                if (
                    not other.appointment_datetime
                    or not other.service_id
                ):
                    continue

                other_start = other.appointment_datetime

                other_duration = (
                    other.service_id.duration or 0.0
                )

                other_end = other_start + timedelta(
                    hours=other_duration
                )

                # Time overlap
                if (
                    new_start < other_end
                    and new_end > other_start
                ):
                    raise ValidationError(
                        f'{record.staff_id.name} already has '
                        f'another appointment during this time.'
                    )