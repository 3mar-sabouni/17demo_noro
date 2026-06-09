from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta


class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'

    parent_id = fields.Many2one('medical.appointment', string="Main Appointment", ondelete='cascade', index=True)
    child_ids = fields.One2many('medical.appointment', 'parent_id', string="Child Appointments")
    inv_ids = fields.One2many('account.move', 'appointment_id', string='Invoices')
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")
    is_service_invoiced = fields.Boolean(string="Service Invoiced",compute="_compute_is_service_invoiced",store=True)
    service_price = fields.Float(string="Service Price")
    service_qty = fields.Integer(string="Service Qty",default=1)
    service_invoice_line_id = fields.Many2one('account.move.line', string="Service Invoice Line",ondelete="set null")
    created_by_group = fields.Selection([
        ('one', 'Reception One'),
        ('two', 'Reception Two'),
    ], string="Reception", default=False)
    mold_ids = fields.One2many('medical.mold', 'appointment_id', string="Medical Molds")
    mold_count = fields.Integer(string="Mold Count", compute="_compute_mold_count", store=True)
    has_mold = fields.Boolean(string="Has Mold", compute="_compute_has_mold", inverse="_inverse_has_mold", store=True)
    type = fields.Selection([
    ('pain', 'Pain'),
    ('cosmetic', 'Cosmetic'),
    ('orthodontic', 'Orthodontics'),
    ('implant', 'Implant'),
    ], string="Type of Appointment")
    reference_id = fields.Many2one('medical.reference', string='Reference')
    mobile = fields.Char('Mobile',related='patient.mobile', readonly=True )
    xray_ids = fields.One2many('medical.xray', 'appointment_id', string="Medical XRays")
    xray_count = fields.Integer(string="XRay Count", compute="_compute_xray_count", store=True)
    has_xray = fields.Boolean(string="Has XRay", compute="_compute_has_xray", inverse="_inverse_has_xray", store=True)
    state = fields.Selection(selection_add=[('main_complate', 'Main Complete')])

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.service_price = self.service_id.lst_price

    @api.depends('mold_ids')
    def _compute_has_mold(self):
        """Compute has_mold based on the existence of related molds."""
        for record in self:
            record.has_mold = bool(record.mold_ids)

    def _inverse_has_mold(self):
        """Ensure 'has_mold' remains True if there are related molds."""
        for record in self:
            if not record.has_mold and record.mold_ids:
                record.has_mold = True  # Reset to True instead of raising an error
                raise UserError("You cannot uncheck 'Has Mold' while related molds exist.")

    @api.depends('mold_ids')
    def _compute_has_mold(self):
        for record in self:
            record.has_mold = bool(record.mold_ids)

    @api.depends('mold_ids')
    def _compute_mold_count(self):
        for record in self:
            record.mold_count = len(record.mold_ids)

    def action_view_molds(self):
        self.ensure_one()
        return {
            'name': 'Medical Molds',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.mold',
            'view_mode': 'tree,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id},
        }


    @api.model
    def create(self, vals):
        # Automatically set the active appointment as the parent if not specified
        if not vals.get('parent_id') and self.env.context.get('active_id'):
            vals['parent_id'] = self.env.context['active_id']
        user = self.env.user
        if user.has_group('dental_management_extension.group_reception_one'):
            vals['created_by_group'] = 'one'
        elif user.has_group('dental_management_extension.group_reception_two'):
            vals['created_by_group'] = 'two'
        return super(MedicalAppointment, self).create(vals)

    def create_invoices(self):
        """ Create or update the existing invoice, ensuring invoicing status is updated via the is_invoiced field. """
        if self.parent_id:
            raise UserError(_("Invoices should be created from the main appointment."))

        # Get existing invoices related to this appointment
        existing_invoices = self.inv_ids  # This is a One2many relation

        invoice = None
        # Check if there's an invoice that's not posted and not canceled
        for existing_invoice in existing_invoices:
            if existing_invoice.state == 'draft':
                invoice = existing_invoice
                break
            elif existing_invoice.state == 'cancel':
                continue  # Ignore canceled invoices

        # If no draft invoice exists, create a new one
        if not invoice:
            invoice_vals = self._prepare_invoice()
            invoice = self.env['account.move'].create(invoice_vals)
            self.inv_ids = [(4, invoice.id)]  # Link invoice to appointment

        # Collect all operations from the main and child appointments
        all_appointments = self | self.child_ids  # Include self and all child appointments

        for appointment in all_appointments:
            # Process each operation separately to assign invoice_line_id
            for line in appointment.operations:
                if line.is_invoiced:
                    continue  # Skip already invoiced operations

                # Create an invoice line individually
                invoice_line = self.env['account.move.line'].create({
                    'product_id': line.description.id,
                    #'price_unit': line.amount,
                    'price_unit': 0,
                    'quantity': 1.0,
                    'name': line.description.name,
                    'move_id': invoice.id,
                })

                # Assign the created invoice line to the operation
                line.write({'is_invoiced': True, 'invoice_line_id': invoice_line.id})

            # Handle service invoicing (ensure it's only invoiced once per appointment)
            if appointment.service_id and not appointment.is_service_invoiced:
                analytic_distribution = appointment.doctor.analytic_distribution if appointment.doctor else {}
                service_invoice_line = self.env['account.move.line'].create({
                    'name': appointment.service_id.name,
                    'product_id': appointment.service_id.id,
                    'price_unit':appointment.service_price or appointment.service_id.lst_price,
                    'quantity': appointment.service_qty or 1,
                    'move_id': invoice.id,
                    'analytic_distribution': analytic_distribution,
                })

                # Mark the service as invoiced and store the invoice line
                appointment.write({
                    'is_service_invoiced': True,
                    'service_invoice_line_id': service_invoice_line.id
                })
        self.invoice_done = True
        return invoice.id
    
    @api.depends('service_invoice_line_id.parent_state','service_invoice_line_id')
    def _compute_is_service_invoiced(self):
        """ 
        Ensure that each appointment (both parent and child) correctly tracks 
        its own service invoicing status without affecting unrelated records.
        """
        for record in self:
            # Check if the current appointment's service is invoiced
            is_invoiced = bool(record.service_invoice_line_id and record.service_invoice_line_id.parent_state != 'cancel')
            record.is_service_invoiced = is_invoiced
    
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([('id', 'in', rec.inv_ids.ids)])

    def action_view_invoice(self):
        """ Open the related invoices. """
        self.ensure_one()

        # Check if there are any related invoices
        if not self.inv_ids:
            return {'type': 'ir.actions.act_window_close'}

        # If there are multiple invoices, open the list view
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',  # Display the list in tree view, and allow form view
            'domain': [('id', 'in', self.inv_ids.ids)],  # Only show the invoices related to this appointment
            'target': 'current',
        }
    
    def action_create_mold(self):
        """Open a popup to create a new mold linked to the current appointment."""
        self.ensure_one()  
        return {
            "type": "ir.actions.act_window",
            "name": "Create Mold",
            "res_model": "medical.mold",
            "view_mode": "form",
            "view_id": self.env.ref("dental_management_extension.view_medical_mold_form").id,  
            "target": "new",  
            "context": {
                "default_appointment_id": self.id,
            },
        }


    def ready(self):
        ready_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if self.has_mold:
            for mold in self.mold_ids:
                if not mold.invoice_id:
                    raise ValidationError(f"Mold {mold.sequence} does not have a related invoice.")
                if mold.invoice_id.payment_state not in ['paid', 'in_payment']:
                    raise ValidationError(f"Invoice {mold.invoice_id.name} for mold {mold.sequence} must be in 'Paid' or 'In Payment' state.")

        if self.has_xray:
            for xray in self.xray_ids:
                if not xray.invoice_id:
                    raise ValidationError(f"XRay {xray.sequence} does not have a related invoice.")
                if xray.invoice_id.payment_state not in ['paid', 'in_payment']:
                    raise ValidationError(f"Invoice {xray.invoice_id.name} for xray {xray.sequence} must be in 'Paid' or 'In Payment' state.")

        self.write({'state': 'ready', 'ready_time': ready_time})
        return True

    
    @api.depends('xray_ids')
    def _compute_xray_count(self):
        for record in self:
            record.xray_count = len(record.xray_ids)

    @api.depends('xray_ids')
    def _compute_has_xray(self):
        for record in self:
            record.has_xray = bool(record.xray_ids)

    def _inverse_has_xray(self):
        for record in self:
            if not record.has_xray and record.xray_ids:
                record.has_xray = True
                raise UserError("You cannot uncheck 'Has XRay' while related XRays exist.")

    def action_view_xrays(self):
        self.ensure_one()
        return {
            'name': 'Medical XRays',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.xray',
            'view_mode': 'tree,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id},
        }

    def action_create_xray(self):
        self.ensure_one()  
        return {
            "type": "ir.actions.act_window",
            "name": "Create XRay",
            "res_model": "medical.xray",
            "view_mode": "form",
            "view_id": self.env.ref("dental_management_extension.view_medical_xray_form").id,
            "target": "new",
            "context": {
                "default_appointment_id": self.id,
                "default_patient_id": self.patient.id,
            },
        }
    @api.constrains('appointment_sdate', 'doctor')
    def _check_unique_doctor_time(self):
        for record in self:
            if record.appointment_sdate and record.doctor:
                # Search for existing appointments at the same time with the same doctor
                overlapping = self.search([
                    ('id', '!=', record.id),  # Exclude the current record during write
                    ('appointment_sdate', '=', record.appointment_sdate),
                    ('doctor', '=', record.doctor.id),
                ])
                if overlapping:
                    raise ValidationError(_("This doctor already has an appointment at the selected time."))
                
    def action_complete_main_appointment(self):
        for rec in self:
            # Search for sub-appointments where parent_id is this record
            sub_appointments = self.search([('parent_id', '=', rec.id)])
            if not sub_appointments:
                raise UserError("No sub-appointments found.")

            # Check if all are in 'done'
            not_done = sub_appointments.filtered(lambda appt: appt.state != 'done')
            if not_done:
                raise UserError("All sub-appointments must be in 'Done' state before confirming this main appointment.")

            # All done — confirm
            rec.state = 'main_complate'