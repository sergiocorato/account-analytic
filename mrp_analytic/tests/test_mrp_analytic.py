# © 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo
from odoo.tests import TransactionCase


class TestMrpAnalytic(TransactionCase):

    def setUp(self):
        super(TestMrpAnalytic, self).setUp()
        self.analytic_account = self.env['account.analytic.account'].create(
            {'name': 'Analytic account test'})
        self.product_category = self.env['product.category'].create({
            'name': 'Test Product category',
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Sale Product',
            'sale_ok': True,
            'type': 'product',
            'categ_id': self.product_category.id,
            'description_sale': 'Test Description Sale',
        })
        self.bom = self.env['mrp.bom'].create(
            {
                'product_id': self.product.id,
                'product_tmpl_id': self.product.product_tmpl_id.id,
            })
        self.production = self.env['mrp.production'].create(
            {
                'product_id': self.product.id,
                'analytic_account_id': self.analytic_account.id,
                'product_uom_id': self.product.uom_id.id,
                'bom_id': self.bom.id,
            })
        self.partner = self.env.ref("base.res_partner_1")

    def test_num_productions(self):
        self.assertEqual(self.analytic_account.num_productions, 1)

    def test_sale_analytic(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'analytic_account_id': self.analytic_account.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': self.product.list_price,
                    'name': self.product.name,
                })
            ],
            'picking_policy': 'direct',
        })
        sale_order.with_context(test_enabled=True).action_confirm()
        manufacturing_order = self.env['mrp.production'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertTrue(manufacturing_order)


@odoo.tests.tagged('post_install', '-at_install')
class TestModuleInstall(TransactionCase):

    def setUp(self):
        super(TestModuleInstall, self).setUp()
        Imm = self.env['ir.module.module']
        self.own_module = Imm.search([('name', '=', 'sale_management')])
        if not self.own_module:
            return False
        self.own_module.button_install()
