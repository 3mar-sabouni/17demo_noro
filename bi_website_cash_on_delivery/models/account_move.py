# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        order_ids = self.env['sale.order'].sudo().search([('invoice_ids.id','in',self.ids)])
        cod_collection = self.env['cod.payment.collection'].sudo().search([('sale_order_id.id','in',order_ids.ids)])
        if order_ids:
            for order in order_ids:
                if order.order_cod_available == True:
                    if cod_collection.ids:
                        for record in cod_collection:
                            if not record.state == 'done':
                                raise ValidationError(_('You can not register payment because COD payment are still pending.'))
                            else:
                                return {
                                    'name': _('Register Payment'),
                                    'res_model': 'account.payment.register',
                                    'view_mode': 'form',
                                    'context': {
                                        'active_model': 'account.move',
                                        'active_ids': self.ids,
                                    },
                                    'target': 'new',
                                    'type': 'ir.actions.act_window',
                                }
                    else:
                        raise ValidationError(_('You can not register payment because COD payment are still pending.'))
                else:
                    return {
                        'name': _('Register Payment'),
                        'res_model': 'account.payment.register',
                        'view_mode': 'form',
                        'context': {
                            'active_model': 'account.move',
                            'active_ids': self.ids,
                        },
                        'target': 'new',
                        'type': 'ir.actions.act_window',
                    }
        else:
            return {
                'name': _('Register Payment'),
                'res_model': 'account.payment.register',
                'view_mode': 'form',
                'context': {
                    'active_model': 'account.move',
                    'active_ids': self.ids,
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }