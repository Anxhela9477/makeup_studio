from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HolidayRequest(models.Model):
    _name = 'makeup_studio.holiday_request'
    _description = 'Staff Holiday Request'
    _rec_name = 'request_code'

    request_code = fields.Char(
        string='Request ID',
        readonly=True,
        copy=False
    )

    staff_id = fields.Many2one(
        'makeup_studio.user',
        string='Staff ID',
        domain=[('role', '=', 'staff')],
        required=True
    )

    start_date = fields.Date(
        string='Start Date',
        required=True
    )

    end_date = fields.Date(
        string='End Date',
        required=True
    )

    reason = fields.Text(
        string='Reason'
    )

    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ],
        string='Status',
        default='pending',
        required=True
    )

    manager_comment = fields.Text(
        string='Manager Comment'
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.request_code = f"HR{record.id:04d}"
        return record

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if (
                record.start_date
                and record.end_date
                and record.end_date < record.start_date
            ):
                raise ValidationError(
                    'End Date cannot be before Start Date.'
                )

    def action_approve(self):
        for record in self:
            record.status = 'approved'

    def action_reject(self):
        for record in self:
            record.status = 'rejected'

    def action_cancel(self):
        for record in self:
            record.status = 'cancelled'