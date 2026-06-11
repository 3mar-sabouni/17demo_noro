from odoo import http, _, fields
from odoo.http import request


class WebsiteSaleSkipAddress(http.Controller):

    @http.route(
        '/shop/custom_confirm_order',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
        methods=['POST']
    )
    def custom_confirm_order(self, **post):
        order_sudo = request.website.sale_get_order()

        if not order_sudo or order_sudo.state != 'draft' or not order_sudo.order_line:
            return request.redirect('/shop/cart')

        customer_name = post.get('customer_name')
        customer_phone = post.get('customer_phone')
        customer_address = post.get('customer_address')

        if not customer_name or not customer_phone or not customer_address:
            return request.redirect('/shop/cart')

        checkout_mode = request.website.account_on_checkout
        is_public_user = request.env.user._is_public()

        if checkout_mode == 'mandatory' and is_public_user:
            return request.redirect('/web/login?redirect=/shop/cart')

        if not is_public_user:
            partner = request.env.user.partner_id.sudo()
            partner.write({
                'name': customer_name,
                'phone': customer_phone,
                'street': customer_address,
            })
        else:
            partner = request.env['res.partner'].sudo().create({
                'name': customer_name,
                'phone': customer_phone,
                'street': customer_address,
            })

        order_sudo.sudo().write({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
        })

        salesperson = request.website.salesperson_id

        if salesperson:
            order_sudo.sudo().activity_schedule(
                activity_type_id=request.env.ref('mail.mail_activity_data_todo').id,
                user_id=salesperson.id,
                note=_(
                    """Order Confirmed by: "%s"
Phone Number: "%s"
Address: "%s" """
                ) % (customer_name, customer_phone, customer_address),
                summary=_("Review Order Confirmation Details"),
                date_deadline=fields.Date.today(),
            )

        order_sudo.sudo().action_confirm()
        request.website.sale_reset()

        msg = request.website.checkout_thank_you_message

        return request.render(
            "ecommerce_skip_delivery_payment.custom_order_confirmation",
            {
                'order': order_sudo,
                'thank_you_message': msg,
            }
        )