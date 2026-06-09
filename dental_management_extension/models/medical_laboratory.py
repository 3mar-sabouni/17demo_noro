from odoo import models,fields,api,_


class Laboratory(models.Model):
    _name = 'medical.laboratory'
    _description = 'Laboratory'

    name = fields.Char(string='Name', required=True)
    sell_price = fields.Float(string='Sell Price', required=True)
    cost_price = fields.Float(string='Cost Price', required=True)
