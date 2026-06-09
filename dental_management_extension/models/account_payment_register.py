# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    analytic_distribution = fields.Json(
        string="Analytic Distribution",
        default=dict,
        help="Passed to the resulting payment; applied to move lines per selection.",
    )
    analytic_apply_on = fields.Selection(
        [
            ("counterpart", "Counterpart lines (receivable/payable)"),
            ("liquidity", "Liquidity lines (bank/cash)"),
            ("all", "All move lines"),
        ],
        string="Apply Analytic On",
        default="counterpart",
    )

    # Required by the analytic_distribution widget
    analytic_precision = fields.Integer(
        string="Analytic Precision",
        default=lambda self: self.env.company.currency_id.decimal_places,
    )

    def _create_payments(self):
        """
        After the base wizard creates the account.payment(s),
        push analytic fields onto them so posting will propagate to move lines.
        """
        payments = super()._create_payments()
        if not payments:
            return payments
        for payment in payments:
            payment.write({
                "analytic_distribution": self.analytic_distribution or {},
                "analytic_apply_on": self.analytic_apply_on or "counterpart",
            })
        return payments
