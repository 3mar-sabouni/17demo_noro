# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_cod = fields.Boolean(string="Is a COD", default=False)

    def _show_in_cart(self):
        # Exclude delivery line from showing up in the cart
        return not self.is_cod and super()._show_in_cart()

class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_cod_available = fields.Boolean('Allow Cash on Delivery For Sale order', default=False)
    is_cod_order = fields.Boolean('COD order', default=False)
    
    amount_cod = fields.Monetary(
        compute='_compute_amount_cod',
        string='COD Amount',
        help="The amount without tax.", store=True, tracking=True)

    @api.depends('order_line.price_unit', 'order_line.tax_id', 'order_line.discount', 'order_line.product_uom_qty')
    def _compute_amount_cod(self):
        for order in self:
            # if self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
            if True:
                order.amount_cod = sum(order.order_line.filtered('is_cod').mapped('price_subtotal'))



class PaymentTransection(models.Model):
    _inherit = "payment.transaction"

    fees = fields.Char(string="fees")
