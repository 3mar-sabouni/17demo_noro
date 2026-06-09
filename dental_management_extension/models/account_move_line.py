from odoo import models, fields, api, _
import logging

# Create a logger for the module
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    # Add a Many2one field to link the invoice with an appointment
    appointment_id = fields.Many2one(
        'medical.appointment',  # Replace with the actual model name for your appointment
        string="Related Appointment",
        ondelete="set null"
    )

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    treatment_id = fields.Many2one('medical.teeth.treatment', string="Related Treatment", ondelete="set null")
    appointment_id = fields.Many2one('medical.appointment', string="Related Appointment", ondelete="set null")

    @api.model
    def create(self, vals):
        """ Ensure invoicing status updates when an invoice line is created. """
        record = super().create(vals)

        if record.treatment_id:
            record.treatment_id._compute_is_invoiced()

        if record.appointment_id:
            record.appointment_id._compute_is_service_invoiced()

        return record

    def unlink(self):
        """ Reset invoicing status if the invoice line is deleted. """
        treatments = self.mapped('treatment_id')
        res = super().unlink()
        treatments._compute_is_invoiced()
        return res

    def write(self, vals):
        """ Update invoicing status when the invoice line state changes. """
        res = super().write(vals)
        if 'parent_state' in vals:
            treatments = self.mapped('treatment_id')
            treatments._compute_is_invoiced()            
        return res
