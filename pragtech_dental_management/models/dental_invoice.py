# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
#from mock import DEFAULT
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class FinancingAgreement(models.Model):
    _inherit = "financing.agreement"
    _description = "Financing Agreement"
    
    invoice_id1 = fields.Many2one('account.move', 'Invoice Number')
    
    @api.model
    def default_get(self, fields):
        res = super(FinancingAgreement, self).default_get(fields)
        invoice_obj = self.env['account.move'].browse(self._context.get('active_ids'))
        if invoice_obj:
            medical_search = self.env['medical.patient'].search([('name', '=', invoice_obj.partner_id.id)])
            res['name'] = medical_search.id
            res['total_amount_to_be_financed'] = invoice_obj.residual
            res['date_of_service'] = invoice_obj.date_invoice
            res['type_of_service'] = ''
            for inv in invoice_obj.invoice_line_ids:
               res['type_of_service'] += inv.product_id.name + ','
            res['invoice_id1'] = invoice_obj.id
            return res
        else:
            return res
    
    @api.model
    def create(self, vals):
        res = super(FinancingAgreement, self).create(vals)
        active_ids = self._context.get('active_ids')
        if active_ids:
            inv_brw = self.env['account.move'].browse(active_ids)
            ret = inv_brw.write({'finance_id': res.id})
        return res
    
class AccountInvoice(models.Model):
    _inherit = "account.move"
    _description = "Account Invoice"
    
    finance_id = fields.Many2one('financing.agreement', 'Financing Agreement')
    dentist = fields.Many2one('medical.physician', 'Dentist')
    insurance_company = fields.Many2one('res.partner', 'Insurance Company',
                                        domain=[('is_insurance_company', '=', True)])
    patient_id = fields.Many2one('res.partner', 'Patient')

    def financial_agreement_action_inherit1(self):
        finance_id = self.finance_id
        if finance_id:
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'financing.agreement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': finance_id.id,
                    'views': [(False, 'form')],
                    }
        else:
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'financing.agreement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(False, 'form')],
                    }
            
    #ORM call connect to JS        
    def fetching_all_invoice_total(self, startDate):
        total_amount = 0
        domain = [('invoice_date', '>=', startDate), ('payment_state', '=', 'paid')]
        invoices = self.env['account.move'].search(domain)
        for invoice in invoices:
            total_amount += invoice.amount_untaxed_signed
        formatted_total_amount = "{:,.2f}".format(total_amount)
        return formatted_total_amount    
    
    #ORM call Connect to JS
    def fetching_all_doctors_revenue(self,startDate):
        doctors_revenue = {}
        domain = [('invoice_date', '>=', startDate), ('payment_state', '=', 'paid')]
        invoices = self.env['account.move'].search(domain)
        
        for invoice in invoices:
            doctor_name = invoice.dentist.name
            if doctor_name not in doctors_revenue:
                doctors_revenue[doctor_name] = 0
            doctors_revenue[doctor_name] += invoice.amount_untaxed_signed
        
        revenue_list = []
        for doctor, revenue in doctors_revenue.items():
            revenue_list.append({'doctor_name': doctor, 'revenue': revenue})
        return revenue_list
