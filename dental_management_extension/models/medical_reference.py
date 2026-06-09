from odoo import models,fields

class MedicalReference(models.Model):
    _name = 'medical.reference'
    _description = 'medical reference'
    
    name = fields.Char('Name')