from odoo import models, fields

class MedicalPhysician(models.Model):
    _name = 'medical.physician'
    _inherit = ['medical.physician', 'analytic.mixin']
    _description = 'Medical Physician with Analytic Accounting'

    
    