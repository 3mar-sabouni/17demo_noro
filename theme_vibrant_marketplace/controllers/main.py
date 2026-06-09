# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import http,tools,api, _
from odoo.http import request
                                                                                                    # from odoo.addons.http_routing.models.ir_http import slug
                                                                                                    # from odoo.addons.website.controllers.main import QueryURL
                                                                                                    # from odoo.addons.website_sale.controllers.main import WebsiteSale

import logging

_logger = logging.getLogger(__name__)

class VibrantWebsiteSale(http.Controller):
    @http.route(['/our/brands'], type='http', auth="public", methods=["GET"], website=True)
    def get_top_brands(self,**post):
        vibrant_conf = request.env['theme.vibrant.fields'].search([('is_active','=','True'),('website_id','=',request.website.id)],limit=1)
        return request.render("theme_vibrant_marketplace.brand_configuration",{"brands":vibrant_conf.brands})