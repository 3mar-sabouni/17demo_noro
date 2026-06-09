from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MedicalMold(models.Model):
    _name = 'medical.mold'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Medical Mold'
    _rec_name = "sequence"

    sequence = fields.Char(string='Mold Sequence', required=True, copy=False, default='New')
    laboratory_id = fields.Many2one('medical.laboratory', string='Laboratory', required=True, tracking=True)
    appointment_id = fields.Many2one('medical.appointment', string='Appointment', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned By', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Send'),
        ('received', 'Received'),
        ('paid', 'Paid'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)

    bill_id = fields.Many2one('account.move', string='Bill', tracking=True, oldname='invoice_id')

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('medical.mold') or 'New'

        mold = super(MedicalMold, self).create(vals)

        if mold.user_id:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_id': mold.id,
                'res_model_id': self.env['ir.model']._get_id('medical.mold'),
                'user_id': mold.user_id.id,
                'summary': _('New Mold Assigned'),
                'note': _('You have been assigned a mold to handle.'),
            })
        return mold

    def write(self, vals):
        if 'user_id' in vals and vals['user_id']:
            for mold in self:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_id': mold.id,
                    'res_model_id': self.env['ir.model']._get_id('medical.mold'),
                    'user_id': vals['user_id'],
                    'summary': _('New Mold Assigned'),
                    'note': _('You have been assigned a mold to handle.'),
                })
        return super(MedicalMold, self).write(vals)

    def action_send(self):
        self.write({'state': 'send'})

    def action_receive(self):
        self.write({'state': 'received'})

    def action_mark_paid(self):
        for mold in self:
            if mold.bill_id and mold.bill_id.payment_state == 'paid':
                mold.state = 'paid'
            else:
                raise UserError(_("Cannot mark as paid: Bill is not paid yet."))

    def action_done(self):
        for mold in self:
            if mold.bill_id and mold.bill_id.payment_state != 'paid':
                raise UserError(_("Cannot mark as done: Bill is not paid."))
            mold.state = 'done'

    def action_create_bill(self):
        """Create a vendor bill for the mold with a predefined purchase service product"""
        product_bill = self.env.ref('dental_management_extension.product_mold_service_vendor', raise_if_not_found=False)
        if not product_bill or not product_bill.sudo().exists():
            product_bill = self.env['product.product'].create({
                'name': 'Mold Service (Vendor)',
                'type': 'service',
                'default_code': 'MOLD-BILL',
                'sale_ok': False,
                'purchase_ok': True,
            })

        for mold in self:
            price = getattr(mold.laboratory_id, 'buy_price', 0.0) \
                or getattr(mold.laboratory_id, 'cost_price', 0.0) \
                or getattr(mold.laboratory_id, 'sell_price', 0.0)

            bill_vals = {
                'move_type': 'in_invoice',  # vendor bill
                'partner_id': False,        # No vendor required anymore
                'invoice_line_ids': [(0, 0, {
                    'product_id': product_bill.id,
                    'quantity': 1,
                    'price_unit': price,
                    'name': product_bill.name,
                })],
            }
            bill = self.env['account.move'].create(bill_vals)
            mold.bill_id = bill.id

        return {
            'name': _('Mold Bill'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.bill_id.id if self.bill_id else bill.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_bill(self):
        self.ensure_one()
        if self.bill_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Bill'),
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.bill_id.id,
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}

    def action_view_invoice(self):
        return self.action_view_bill()
