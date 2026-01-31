from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    x_cliente_ativo = fields.Boolean(
        string='Cliente Ativo',
        default=False,
    )