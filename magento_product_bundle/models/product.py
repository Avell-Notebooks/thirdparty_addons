# -*- coding: utf-8 -*-
# © 2018 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    attribute_value_id = fields.Many2one(
        string="Attributo Relacionado",
        comodel_name="product.attribute.value",
        ondelete="restrict",
        help="Armazena o valor de attributo que representa esse componente.",
    )
