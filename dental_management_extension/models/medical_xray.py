from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class MedicalXRay(models.Model):
    _name = 'medical.xray'
    _description = 'MEdical X-Ray'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "sequence"

    sequence = fields.Char(string='X-ray Sequence', required=True, copy=False,default='New')
    patient_id = fields.Many2one('medical.patient','Patient')
    xray_type = fields.Many2one('medical.xray.type')
    appointment_id = fields.Many2one('medical.appointment', string='Appointment', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Canceled')
    ], string='Status', default='draft', tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', tracking=True)

    @api.model
    def create(self, vals):
        """Override create method to assign sequence number and create an activity"""
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('medical.xray') or 'New'
        xray = super(MedicalXRay, self).create(vals)
        return xray

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_create_invoice(self):
        for record in self:
            if not record.xray_type or not record.xray_type.product_id:
                raise UserError("Please set a product in the X-ray type before creating an invoice.")

            product = record.xray_type.product_id
            partner = record.patient_id.partner_id
            if not partner and record.appointment_id and record.appointment_id.patient:
                partner = record.appointment_id.patient.partner_id
            if not partner:
                raise UserError("Missing patient (customer) for invoicing.")

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_origin': record.sequence,
                'invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'quantity': 1,
                    'price_unit': product.list_price,
                    'name': product.name,
                    'account_id': product.categ_id.property_account_income_categ_id.id or
                                product.property_account_income_id.id,
                })],
            }

            invoice = self.env['account.move'].create(invoice_vals)
            record.invoice_id = invoice.id

            return {
                'name': 'Invoice',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoice.id,
                'target': 'current',
            }
        
    def action_view_invoice(self):
        """Open the related invoice directly."""
        self.ensure_one()
        if self.invoice_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.invoice_id.id,
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}

class MEdicalXRay(models.Model):
    _name = 'medical.xray.type'
    _description = 'MEdical XRay Type'
    
    name = fields.Char('Name')
    product_id = fields.Many2one('product.template')