# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http, tools, SUPERUSER_ID, _
from odoo.http import request
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
_logger = logging.getLogger(__name__)

from odoo.addons.website_sale.controllers.main import WebsiteSale, PaymentPortal
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment import utils as payment_utils

class WebsiteCODPayment(http.Controller):

    _accept_url = '/cod/payment/feedback'

    @http.route(['/cod/payment/feedback'], type='http', auth='none', csrf=False)
    def cod_form_feedback(self, **post):
        post.update({ 'return_url':'/shop/payment/validate' })
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('cod', post)
        acquirer_sudo = tx_sudo.provider_id
        request.env['payment.transaction'].sudo()._handle_notification_data('cod', post)
        return werkzeug.utils.redirect(post.pop('return_url', '/'))
    
    
    @http.route('/shop/payment/cod', type='json', auth="public", methods=['POST'], website=True)
    def codline(self, payment_id, **post):
        return True
    
    @http.route('/shop/payment/default', type='json', auth="public", methods=['POST'], website=True)
    def payment_default(self, payment_id, **post):      
        
        cr, uid, context = request.cr, request.uid, request.context
        
        return request.redirect('/shop/payment/validate')


class WebsiteCODPayment(WebsiteSale):

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                # Retrieve the last known order from the session if the session key `sale_order_id`
                # was prematurely cleared. This is done to prevent the user from updating their cart
                # after payment in case they don't return from payment through this route.
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
            if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.with_context(send_email=True).action_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            order.action_cancel()
        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        if tx.provider_id.code == 'cod':
            payment_acquirer_obj = request.env['payment.provider'].sudo().search([('id','=', tx.provider_id.id)]) 
            order.order_cod_available = True
            product_obj = request.env['product.product']
            extra_fees_product = request.env.ref('bi_website_cash_on_delivery.product_product_fees').id
            product_ids = product_obj.sudo().search([('product_tmpl_id.id', '=', extra_fees_product)])
            order_line_obj = request.env['sale.order.line'].sudo().search([])
            
            
            flag = 0
            for i in order_line_obj:
                if i.product_id.id == product_ids.id and i.order_id.id == order.id:
                    flag = flag + 1
            if flag == 0:
                tx.update({
                    'fees' : payment_acquirer_obj.delivery_fees
                    })   

            order1 = order.sudo()         

            order.action_confirm()
            email_act = order.action_quotation_send()
            email_ctx = email_act.get('context', {})

            mail_template = order1._get_confirmation_template()
            order._send_order_notification_mail(mail_template)
            request.website.sale_reset()            

        return request.redirect('/shop/confirmation')

    @http.route(['/shop/update_provider'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_provider(self, **post):
        order = request.website.sale_get_order()
        if order is None:
            if not order and 'sale_last_order_id' in request.session:
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        order_line_obj = request.env['sale.order.line']
        provider_id = post.get('provider_id')

        product_obj = request.env['product.product']
        extra_fees_product = request.env.ref('bi_website_cash_on_delivery.product_product_fees').id
        product_ids = product_obj.sudo().search([('product_tmpl_id.id', '=', extra_fees_product)])
        payment_acquirer_obj = request.env['payment.provider'].sudo().search([('code','=', 'cod')],limit=1) 
        line_ids = request.env['sale.order.line'].sudo().search([('order_id','=',order.id),('is_cod','=',True)],limit=1)
        if provider_id == 'cod':
            if not order.id:
                pass
            if not line_ids:
                order_line_obj.sudo().create({
                            'product_id': product_ids.id,
                            'name': 'Extra Fees',
                            'price_unit': payment_acquirer_obj.delivery_fees,
                            'order_id': order.id,
                            'product_uom':product_ids.uom_id.id,
                            'is_cod':True
                        })
            else:
                if line_ids.price_unit != payment_acquirer_obj.delivery_fees:
                    line_ids.sudo().update({'price_unit': payment_acquirer_obj.delivery_fees,})
        else:
            line_ids.sudo().unlink()

        return self._update_website_sale_cod_return(order, **post)

    def _update_website_sale_cod_return(self, order, **post):
        Monetary = request.env['ir.qweb.field.monetary']
        provider_id = (post.get('provider_id'))
        currency = order.currency_id
        if order:
            return {
                'provider_id': provider_id,
                'new_amount_cod': Monetary.value_to_html(order.amount_cod, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
                'new_amount_total_raw': order.amount_total,
            }
        return {}

class PaymentPortalCod(PaymentPortal):

    @http.route(
        '/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True
    )
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The sales order to pay, as a `sale.order` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError(_("The access token is invalid."))

        if order_sudo.state == "cancel":
            raise ValidationError(_("The order has been canceled."))

        kwargs.update({
            'partner_id': order_sudo.partner_invoice_id.id,
            'currency_id': order_sudo.currency_id.id,
            'sale_order_id': order_id,  # Include the SO to allow Subscriptions to tokenize the tx
        })
        if not kwargs.get('amount'):
            kwargs['amount'] = order_sudo.amount_total
        if order_sudo.order_line.filtered('is_cod'):
            kwargs['amount'] = order_sudo.amount_total
        if tools.float_compare(kwargs['amount'], order_sudo.amount_total, precision_rounding=order_sudo.currency_id.rounding) and not order_sudo.order_line.filtered('is_cod'):
            raise ValidationError(_("The cart has been updated. Please refresh the page."))

        tx_sudo = self._create_transaction(
            custom_create_values={'sale_order_ids': [Command.set([order_id])]}, **kwargs,
        )

        # Store the new transaction into the transaction list and if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        last_tx_id = request.session.get('__website_sale_last_tx_id')

        request.session['__website_sale_last_tx_id'] = tx_sudo.id

        self._validate_transaction_for_order(tx_sudo, order_id)

        return tx_sudo._get_processing_values()

               
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
