# © 2020 Mackilem Van der Laan, Goiaba Intelligence
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent, Component
from odoo import fields
import logging

_logger = logging.getLogger(__name__)


class MagentoImporter(AbstractComponent):
    _inherit = 'magento.importer'

    def _must_skip(self):
        skip = super(MagentoImporter, self)._must_skip()
        if self.magento_record.get('type') == 'bundle':
            skip = "Produto Cadastrado em 'magento_product_dundle'"
        return skip


class SaleOrderAdapter(Component):
    _inherit = 'magento.sale.order.adapter'

    def read(self, external_id, attributes=None):
        data = super(SaleOrderAdapter, self).read(external_id, attributes)

        if self.collection.version == '1.7' and data.get('items'):
            data = self._convert_bundle_to_product_template(data)
        return data

    def _convert_bundle_to_product_template(self, resource):
        """
        This method turns bundle products into a product template.
        :Components with '#' must match with Odoo Variants. If does not
         match, the bundle product won't be import.
        :Components with '!#', will be not import.
         ::returns: resource updated
         ::type: magento dict
        """
        prod_tmpl_obj = self.env['product.template']
        prod_tmpl_attr_obj = self.env['product.template.attribute.value']
        magento_product_obj = self.env['magento.product.product']

        for item in resource['items']:
            if item.get('sku', '')[0] in ['n', 'N']:  # Identifica o Notebook
                attributes = []
                codes = item.get('sku').split('-')
                notebook_sku = codes.pop(0)
                for attr in codes:
                    if attr[0] == '#':
                        attributes.append(attr)
                    elif attr[:2] == '!#':
                        continue
                    else:
                        resource.setdefault("after_products", []).append(attr)

                prod_tmpl = prod_tmpl_obj.search(
                    [('magento_code_tmpl', '=', notebook_sku)],
                    limit=1)
                domain = [
                    ('magento_code_attrs', 'in', attributes),
                    ('product_tmpl_id', '=', prod_tmpl.id)]
                combination = prod_tmpl_attr_obj.search(domain)

                # Only accepted if there are attrs and match the total lines
                match = len(combination) == len(prod_tmpl.attribute_line_ids)

                if combination and match:
                    notebook = prod_tmpl._create_product_variant(combination)
                    notebook.magento_code = item.get('sku')
                    magento_product_obj.create({
                        'odoo_id': notebook.id,
                        'backend_id': 1,
                        'external_id': item['product_id'],
                        'created_at': fields.Date.today(),
                        'product_type': 'simple',
                        'no_stock_sync': True})
                else:
                    _logger.debug("This product does not match the attributes")

        return resource


class SaleOrderImporter(Component):
    _inherit = 'magento.sale.order.importer'

    def _after_import(self, binding):
        res = super(SaleOrderImporter, self)._after_import(binding)
        sale = binding.odoo_id
        after_products = self._map_data().source.get('after_products')
        if after_products and sale and sale._name == "sale.order":
            for code in after_products:
                domain = [('default_code', '=', code)]
                product = self.env['product.product'].search(domain, limit=1)
                if product:
                    line_vals = {
                        'product_id': product.id,
                        'order_id': sale.id,
                        'name': product.name,
                        'customer_lead': 0,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': 1,
                        'price_unit': 0}
                    sale.write({'order_line': [(0, 0, line_vals)]})
                else:
                    _logger.debug("Não foi possível encontrar\
                                  o produto [{}]".format(code))
        return res
