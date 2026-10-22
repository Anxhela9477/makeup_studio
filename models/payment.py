from odoo import models, fields
from odoo.exceptions import ValidationError


class MakeupPayment(models.Model):
    _name = 'makeup_studio.payment'
    _description = 'Makeup Studio Payment'
    loyalty_points_deducted = fields.Boolean(
        string='Loyalty Points Deducted',
        default=False,
        readonly=True
    )

    appointment_id = fields.Many2one(
        'makeup_studio.appointment',
        string='Appointment',
        required=True
    )

    client_id = fields.Many2one(
        related='appointment_id.client_id',
        string='Client',
        store=True,
        readonly=True
    )

    amount = fields.Float(
        related='appointment_id.final_price',
        string='Amount to Pay',
        store=True,
        readonly=True
    )

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer')
    ], string='Payment Method', required=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], string='Payment Status', default='unpaid', required=True)

    payment_date = fields.Datetime(
        string='Payment Date'
    )

    transaction_reference = fields.Char(
        string='Transaction Reference'
    )

    loyalty_points_awarded = fields.Boolean(
        string='Loyalty Points Awarded',
        default=False,
        readonly=True
    )

    points_earned = fields.Integer(
        string='Points Earned',
        default=0,
        readonly=True
    )

    def action_mark_paid(self):
        for record in self:

            if record.payment_status == 'paid':
                raise ValidationError(
                    'This payment is already marked as Paid.'
                )

            record.payment_status = 'paid'
            record.payment_date = fields.Datetime.now()

            record._process_loyalty_points()

    def _process_loyalty_points(self):
        for record in self:

            appointment = record.appointment_id

            # Payment must be paid
            if record.payment_status != 'paid':
                return

            # Appointment must be completed
            if appointment.status != 'completed':
                return


            if not record.loyalty_points_deducted:

                points_used = appointment.loyalty_points_used

                if points_used > 0:

                    if record.client_id.loyalty_points < points_used:
                        raise ValidationError(
                            'The client does not have enough loyalty points.'
                        )

                    record.client_id.loyalty_points -= points_used

                record.loyalty_points_deducted = True

            # -----------------------------------------------------
            # AWARD NEW LOYALTY POINTS
            # -----------------------------------------------------

            if record.loyalty_points_awarded:
                return

            # Minimum purchase = €30
            if record.amount < 30:
                record.loyalty_points_awarded = True
                return

            # €10 spent = 1 loyalty point
            points = int(record.amount // 10)

            record.client_id.loyalty_points += points

            record.points_earned = points
            record.loyalty_points_awarded = True