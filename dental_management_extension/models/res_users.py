from odoo import models,fields

class ResUsers(models.Model):
    _inherit='res.users'
    _description = "Res Users"

    doctor_ids = fields.Many2many('medical.physician', string='Doctors')