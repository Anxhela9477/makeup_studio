from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MakeupInventory(models.Model):
    _name = 'makeup_studio.inventory'
    _description = 'Makeup Studio Inventory'
    _rec_name = 'product_name'

    inventory_code = fields.Char(
        string='Product ID',
        readonly=True,
        copy=False
    )

    product_name = fields.Char(
        string='Product Name',
        required=True
    )

    category = fields.Selection([
        ('foundation', 'Foundation'),
        ('concealer', 'Concealer'),
        ('powder', 'Powder'),
        ('blush', 'Blush'),
        ('bronzer', 'Bronzer'),
        ('highlighter', 'Highlighter'),
        ('eyeshadow', 'Eyeshadow'),
        ('eyeliner', 'Eyeliner'),
        ('mascara', 'Mascara'),
        ('lipstick', 'Lipstick'),
        ('brushes', 'Brushes'),
        ('skincare', 'Skincare'),
        ('other', 'Other')
    ],
        string='Category',
        required=True,
        default='other'
    )

    quantity = fields.Integer(
        string='Quantity in Stock',
        default=0,
        required=True
    )

    minimum_quantity = fields.Integer(
        string='Minimum Stock',
        default=5,
        required=True
    )

    unit_price = fields.Float(
        string='Unit Price (€)',
        default=0.0
    )

    total_value = fields.Float(
        string='Stock Value (€)',
        compute='_compute_total_value',
        store=True
    )

    low_stock = fields.Boolean(
        string='Low Stock',
        compute='_compute_low_stock',
        store=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    notes = fields.Text(
        string='Notes'
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)

        record.inventory_code = f"INV{record.id:04d}"

        return record

    @api.depends('quantity', 'unit_price')
    def _compute_total_value(self):
        for record in self:
            record.total_value = (
                record.quantity * record.unit_price
            )

    @api.depends('quantity', 'minimum_quantity')
    def _compute_low_stock(self):
        for record in self:
            record.low_stock = (
                record.quantity <= record.minimum_quantity
            )

    @api.constrains(
        'quantity',
        'minimum_quantity',
        'unit_price'
    )
    def _check_inventory_values(self):
        for record in self:

            if record.quantity < 0:
                raise ValidationError(
                    'Quantity cannot be negative.'
                )

            if record.minimum_quantity < 0:
                raise ValidationError(
                    'Minimum stock cannot be negative.'
                )

            if record.unit_price < 0:
                raise ValidationError(
                    'Unit price cannot be negative.'
                )