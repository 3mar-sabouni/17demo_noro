# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    analytic_distribution = fields.Json(
        string="Analytic Distribution",
        default=dict,
        help="Split this payment over analytic accounts; the distribution is copied to the resulting journal items when the payment is posted.",
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

    # ---- Classification helpers ----
    @api.model
    def _is_liquidity_account(self, account):
        """
        Liquidity in your setup = Bank and Cash only.
        """
        atype = getattr(account, "account_type", False)
        if atype:
            return atype == "asset_cash"   # <-- only this
        # Legacy fallback (older schemas sometimes store on user_type_id.type)
        if account.user_type_id and hasattr(account.user_type_id, "type"):
            return account.user_type_id.type in {"liquidity", "cash"}  # safe fallback
        return False

    @api.model
    def _is_arap_account(self, account):
        atype = getattr(account, "account_type", False)
        if atype:
            return atype in {"asset_receivable", "liability_payable"}
        if account.user_type_id and hasattr(account.user_type_id, "type"):
            return account.user_type_id.type in {"receivable", "payable"}
        return False

    # ---- Core application logic ----
    def _apply_distribution_to_line_vals(self, line_vals):
        """Attach analytic_distribution to line_vals if they match selection."""
        self.ensure_one()
        if not self.analytic_distribution:
            return line_vals

        account_id = line_vals.get("account_id")
        if not account_id:
            return line_vals

        account = self.env["account.account"].browse(account_id)
        is_liquidity = self._is_liquidity_account(account)
        is_arap = self._is_arap_account(account)

        sel = self.analytic_apply_on
        should_apply = (
            sel == "all"
            or (sel == "liquidity" and is_liquidity)
            or (sel == "counterpart" and is_arap)  # <— ONLY AR/AP now
        )
        if should_apply:
            line_vals["analytic_distribution"] = dict(self.analytic_distribution)
        return line_vals

    def _prepare_move_values(self, **optional_values):
        """Apply during initial move dict construction."""
        self.ensure_one()
        res = super()._prepare_move_values(**optional_values)
        if not self.analytic_distribution:
            return res

        updated = []
        for cmd in res.get("line_ids", []):
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == 0:
                vals = dict(cmd[2])
                vals = self._apply_distribution_to_line_vals(vals)
                updated.append((0, 0, vals))
            else:
                updated.append(cmd)
        res["line_ids"] = updated
        return res

    def _synchronize_to_moves(self, changed_fields):
        """
        Also enforce after the move exists (covers recomputations/edits).
        """
        res = super()._synchronize_to_moves(changed_fields)
        for payment in self:
            if not payment.analytic_distribution or not payment.move_id:
                continue
            for line in payment.move_id.line_ids:
                account = line.account_id
                is_liquidity = payment._is_liquidity_account(account)
                is_arap = payment._is_arap_account(account)
                sel = payment.analytic_apply_on
                if (
                    sel == "all"
                    or (sel == "liquidity" and is_liquidity)
                    or (sel == "counterpart" and is_arap)
                ):
                    line.analytic_distribution = dict(payment.analytic_distribution)
        return res
