from odoo import models, fields


class MakeupDiscount(models.Model):
    _name = 'makeup_studio.discount'
    _description = 'Makeup Studio Discount'

    name = fields.Char(
        string='Discount Name',
        required=True
    )

    minimum_points = fields.Integer(
        string='Minimum Loyalty Points',
        required=True,
        default=0
    )

    discount_amount = fields.Float(
        string='Discount Amount (€)',
        required=True,
        default=0.0
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )