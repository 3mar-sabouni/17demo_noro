from odoo import models,fields,api,_


class MedicalTeethTreatment(models.Model):
    _inherit = "medical.teeth.treatment"

    invoice_line_id = fields.Many2one(
        'account.move.line', string="Invoice Line", ondelete="set null"
    )
    is_invoiced = fields.Boolean(
        string="Is Invoiced",
        compute="_compute_is_invoiced",
        store=True
    )

    @api.depends('invoice_line_id.parent_state')
    def _compute_is_invoiced(self):
        """ Mark treatment as invoiced if its invoice line exists and is not canceled. """
        for record in self:
            record.is_invoiced = bool(record.invoice_line_id and record.invoice_line_id.parent_state != 'cancel')
