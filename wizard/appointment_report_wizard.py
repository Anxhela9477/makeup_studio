from odoo import models, fields
from odoo.exceptions import ValidationError


class AppointmentReportWizard(models.TransientModel):
    _name = 'makeup_studio.appointment_report_wizard'
    _description = 'Appointment Report Wizard'

    date_from = fields.Date(
        string='Start Date',
        required=True
    )

    date_to = fields.Date(
        string='End Date',
        required=True
    )

    staff_id = fields.Many2one(
        'makeup_studio.user',
        string='Staff Member',
        domain=[('role', 'in', ['staff', 'manager'])]
    )

    status = fields.Selection([
        ('all', 'All'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='all', required=True)

    def action_generate_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise ValidationError(
                'Start Date cannot be after End Date.'
            )

        # Filter appointments by the selected date range
        date_from = fields.Datetime.to_string(
            fields.Datetime.start_of(
                fields.Datetime.to_datetime(self.date_from), 'day'
            )
        )
        date_to = fields.Datetime.to_string(
            fields.Datetime.end_of(
                fields.Datetime.to_datetime(self.date_to), 'day'
            )
        )

        domain = [
            ('appointment_datetime', '>=', date_from),
            ('appointment_datetime', '<=', date_to),
        ]

        # Optional staff filter
        if self.staff_id:
            domain.append(('staff_id', '=', self.staff_id.id))

        # Optional appointment status filter
        if self.status != 'all':
            domain.append(('status', '=', self.status))

        appointments = self.env['makeup_studio.appointment'].search(
            domain,
            order='appointment_datetime asc'
        )

        return self.env.ref(
            'makeup_studio.action_report_appointment'
        ).report_action(appointments)
