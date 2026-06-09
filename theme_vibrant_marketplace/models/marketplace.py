# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MarketPlace(models.Model):
    _inherit = "theme.vibrant.fields"

    brands = fields.Many2many(comodel_name="vibrant.brands",string="Brands",help="Choose the brnads to show")

class VibrantBrands(models.Model):
    _name = "vibrant.brands"

    name = fields.Char("Name",help="Enter the name of Brand")
    image = fields.Binary("Image",help="Choose an brand image")

# class ProductTemplate(models.Model):
#     _inherit = "product.template"

#     activate_deal = fields.Boolean("Activate Lightning Deal")
#     original_price = fields.Float("Original Price")
    
#     @api.onchange('activate_deal')
#     def set_list_price(self):
#         if self.activate_deal:
#             self.original_price = self.list_price
#         else:
#             self.original_price = False
