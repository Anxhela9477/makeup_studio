from odoo import models, fields


class MakeupStudioService(models.Model):
    _name = 'makeup_studio.service'
    _description = 'Makeup Studio Service'

    name = fields.Char(
        string='Service Name',
        required=True
    )

    price = fields.Float(
        string='Price',
        required=True
    )

    description = fields.Text(
        string='Description'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )
    duration = fields.Float(
        string='Duration (Hours)',
        default=1.0
    )
    material_ids = fields.One2many(
        'makeup_studio.service_material',
        'service_id',
        string='Materials'
    )
    quantity_used = fields.Float(
        string='Quantity Used',
        required=True,
        default=1.0
    )