# © 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestMrpAnalytic(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_account = cls.env['account.analytic.account'].create(
            {'name': 'Analytic account test'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.bom = cls.env['mrp.bom'].create(
            {
                'product_id': cls.product.id,
                'product_tmpl_id': cls.product.product_tmpl_id.id,
            })
        cls.production = cls.env['mrp.production'].create(
            {
                'product_id': cls.product.id,
                'analytic_account_id': cls.analytic_account.id,
                'product_uom_id': cls.product.uom_id.id,
                'bom_id': cls.bom.id,
            })
        cls.partner = cls.env.ref("base.res_partner_1")

    def test_num_productions(self):
        self.assertEqual(self.analytic_account.num_productions, 1)

    def test_sale_analytic(self):
        module = self.env['ir.module.module'].search(
            [('name', '=', 'sale_management')])
        if not module:
            return False
        module.button_install()

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
