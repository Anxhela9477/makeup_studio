from odoo import models, fields


class MakeupServiceMaterial(models.Model):
    _name = 'makeup_studio.service_material'
    _description = 'Service Material'

    service_id = fields.Many2one(
        'makeup_studio.service',
        string='Service',
        required=True,
        ondelete='cascade'
    )

    inventory_id = fields.Many2one(
        'makeup_studio.inventory',
        string='Inventory Product',
        required=True
    )

    quantity_used = fields.Float(
        string='Quantity Used',
        required=True,
        default=1.0
    )