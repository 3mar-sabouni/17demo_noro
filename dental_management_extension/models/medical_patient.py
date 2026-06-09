from odoo import models,_,fields
from odoo.exceptions import UserError, ValidationError

class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    barcode = fields.Char(string='Barcode')

    def create_lines(self, treatment_lines, patient_id, appt_id):
        # create objects
        medical_teeth_treatment_obj = self.env['medical.teeth.treatment']
        medical_physician_obj = self.env['medical.physician']
        product_obj = self.env['product.product']
        teeth_code_obj = self.env['teeth.code']
        # delete previous records
        patient = int(patient_id)
        patient_brw = self.env['medical.patient'].browse(patient)
        partner_brw = patient_brw.partner_id
        if appt_id:
            prev_appt_operations = medical_teeth_treatment_obj.search(
                [('appt_id', '=', int(appt_id)), ('state', '!=', 'completed')])
            # prev_appt_operations.unlink()
        else:
            prev_pat_operations = medical_teeth_treatment_obj.search(
                [('patient_id', '=', int(patient_id)), ('state', '!=', 'completed')])
            # prev_pat_operations.unlink()

        prev_pat_missing_operations = medical_teeth_treatment_obj.search(
            [('patient_id', '=', int(patient_id)), ('state', '!=', 'completed')])
        for each_prev_pat_missing_operations in prev_pat_missing_operations:
            if each_prev_pat_missing_operations.description.action_perform == 'missing':
                pass
                # each_prev_pat_missing_operations.unlink()
        if treatment_lines:
            current_physician = 0
            for each in treatment_lines:
                if each.get('prev_record') == 'false':
                    all_treatment = each.get('values')
                    if all_treatment:
                        for each_trt in all_treatment:

                            vals = {}
                            category_id = int(each_trt.get('categ_id'))
                            vals['description'] = category_id
                            if 1:
                                if (str(each.get('teeth_id')) != 'all'):
                                    actual_teeth_id = teeth_code_obj.search(
                                        [('internal_id', '=', int(each.get('teeth_id')))])
                                    vals['teeth_id'] = actual_teeth_id[0].id
                                vals['patient_id'] = patient
                                # desc = ''
                                # for each_val in each_trt['values']:
                                #     if each_val:
                                #         desc += each_val + ' '
                                # vals['detail_description'] = desc
                                vals['detail_description'] = each_trt['values']
                                vals['selected_area'] = each.get('selected_area')
                                vals['treatment_id'] = each_trt.get('categ_id')
                                dentist = each.get('dentist')
                                if dentist:
                                    physician = medical_physician_obj.search([('name', '=', dentist)])
                                    if physician:
                                        dentist = physician.id
                                        vals['dentist'] = dentist
                                        current_physician = 1
                                status = ''
                                if each.get('status_name') and each.get('status_name') != 'false':
                                    status_name = each.get('status_name')
                                    status = (str(each.get('status_name')))
                                    if status_name == 'in_progress':
                                        status = 'in_progress'
                                    elif status_name == 'planned':
                                        status = 'planned'
                                else:
                                    status = 'planned'
                                vals['state'] = status
                                vals['date'] = each['date']
                                p_brw = product_obj.browse(vals['description'])
                                vals['amount'] = p_brw.lst_price
                                if appt_id:
                                    vals['appt_id'] = appt_id
                                treatment_id = medical_teeth_treatment_obj.create(vals)
                                if each.get('multiple_teeth'):
                                    full_mouth = each.get('multiple_teeth')
                                    full_mouth = full_mouth.split('_')
                                    operate_on_tooth = []
                                    for each_teeth_from_full_mouth in full_mouth:
                                        actual_teeth_id = teeth_code_obj.search(
                                            [('internal_id', '=', int(each_teeth_from_full_mouth))])
                                        operate_on_tooth.append(actual_teeth_id.id)
                                        treatment_id.write({'teeth_code_rel': [(6, 0, operate_on_tooth)]})
                elif each.get('prev_record') == 'true':
                    all_treatment = each.get('values')
                    if all_treatment:
                        for each_trt in all_treatment:
                            vals = {}
                            dentist = each.get('dentist')
                            if dentist:
                                physician = medical_physician_obj.search([('name', '=', dentist)])
                                if physician:
                                    dentist = physician.id
                                    vals['dentist'] = dentist
                                    current_physician = 1
                        
                            select = str(each.get('selected_area'))
                            teeth_idsss = each.get('teeth_id')
                            mutiple_teeeth_po = each.get('multiple_teeth')

                            for each in treatment_lines:
                                categ_id = each['values'][0]['categ_id'] 
                                detail_description = each['values'][0]['values'] 
                                
                                # Search for all treatment records matching selected_area, teeth_id, and categ_id
                                if teeth_idsss == 'all':
                                    treatment_records_full = medical_teeth_treatment_obj.search([
                                    ('detail_description', '=',detail_description),
                                    ('patient_id', '=', patient_id),
                                    # ('teeth_id', '=',each.get('teeth_id')),
                                    ('treatment_id','=', categ_id),
                                     ])
                                    status = each.get('status_name') if each.get('status_name') in ['completed', 'in_progress', 'planned'] else 'planned'
                                    
                                    # Update the state for all matching records
                                    treatment_records_full.write({'state': status})
                                else:
                                    
                                    treatment_records = medical_teeth_treatment_obj.search([
                                        ('selected_area', '=', each.get('selected_area')),
                                        ('teeth_id', '=', each.get('teeth_id')),
                                        ('patient_id', '=', patient_id),
                                        ('treatment_id', '=', categ_id),
                                    ])
                                    status = each.get('status_name') if each.get('status_name') in ['completed', 'in_progress', 'planned'] else 'planned'
                                    
                                    # Update the state for all matching records
                                    treatment_records.write({'state': status})                     
                # elif each.get('prev_record') == 'true':
                #     all_treatment = each.get('values')
                #     if all_treatment:
                #         for each_trt in all_treatment:
                #             select = str(each.get('selected_area'))
                #             treatment_records = medical_teeth_treatment_obj.search([('selected_area', '=',select)])
                #             for treetments in treatment_records:
                #                 treetments.state = each.get('status_name')
                                        
                
            # cr.execute('insert into teeth_code_medical_teeth_treatment_rel(operation,teeth) values(%s,%s)' % (treatment_id,each_teeth_from_full_mouth))
            invoice_vals = {}
            invoice_line_vals = []
            
            # Creating invoice lines
            # get account id for products
            jr_search = self.env['account.journal'].search(
                [('type', '=', 'sale'), ('company_id', '=', self.env.company.id)])
            if not jr_search:
                raise UserError(_('Kindly Configure the Sales Journal for Invoicing.'))

            jr_brw = jr_search
            for each in treatment_lines:
                if each.get('prev_record') == 'false':
                    if str(each.get('status_name')).lower() == 'completed':

                        for each_val in each['values']:
                            each_line = []
                            product_dict = {}
                            product_dict['product_id'] = int(each_val['categ_id'])
                            p_brw = product_obj.browse(int(each_val['categ_id']))
                            if p_brw.action_perform != 'missing':
                                # desc = ''
                                # features = ''
                                # for each_v in each_val['values']:
                                #     if each_v:
                                #         desc = str(each_v)
                                #         features += desc + ' '
                                if (each['teeth_id'] != 'all'):
                                    actual_teeth_id = teeth_code_obj.search(
                                        [('internal_id', '=', int(each.get('teeth_id')))])
                                    invoice_name = actual_teeth_id.name_get()
                                    product_dict['surface'] = each.get('selected_area')

                                    product_dict['name'] = str(invoice_name[0][1]) + ' ' + each_val['values']
                                else:
                                    product_dict['name'] = 'Full Mouth'
                                product_dict['quantity'] = 1
                                product_dict['price_unit'] = p_brw.lst_price
                                acc_obj = self.env['account.account'].search(
                                    [('name', '=', 'Local Sales'), ('account_type', '=', 'Income')], limit=1)
                                for account_id in jr_brw:
                                    # product_dict['account_id'] = account_id.payment_debit_account_id.id if account_id.payment_debit_account_id else acc_obj.id
                                    '''
                                        V15 payment_debit_account_id Field is deprecated. Currently adding Default account. This need to be fixed later
                                        with new v15 build features.
                                    '''
                                    product_dict['account_id'] = account_id.default_account_id.id if account_id.default_account_id else acc_obj.id
                                each_line.append(product_dict)
                                invoice_line_vals.append(each_line)
                            # Creating invoice dictionary
                            # invoice_vals['account_id'] = partner_brw.property_account_receivable_id.id
                            if patient_brw.current_insurance:
                                invoice_vals['partner_id'] = patient_brw.current_insurance.company_id.id
                            else:
                                invoice_vals['partner_id'] = partner_brw.id
                            invoice_vals['patient_id'] = partner_brw.id
                            # invoice_vals['partner_id'] = partner_brw.id
                            if current_physician:
                                invoice_vals['dentist'] = physician[0].id
                            invoice_vals['move_type'] = 'out_invoice'
                            invoice_vals['insurance_company'] = patient_brw.current_insurance.company_id.id
                            # invoice_vals['invoice_line_ids'] = invoice_line_vals                
                
                elif each.get('prev_record') == 'true':                    
                    if str(each.get('status_name')).lower() == 'completed':
                        for each_val in each['values']:
                            each_line = []
                            product_dict = {}
                            product_dict['product_id'] = int(each_val['categ_id'])
                            p_brw = product_obj.browse(int(each_val['categ_id']))
                            if p_brw.action_perform != 'missing':
                                # desc = ''
                                # features = ''
                                # for each_v in each_val['values']:
                                #     if each_v:
                                #         desc = str(each_v)
                                #         features += desc + ' '
                                if (each['teeth_id'] != 'all'):
                                    actual_teeth_id = teeth_code_obj.search(
                                        [('internal_id', '=', int(each.get('teeth_id')))])
                                    invoice_name = actual_teeth_id.name_get()
                                    product_dict['surface'] = each.get('selected_area')                            
                                    product_dict['name'] = str(invoice_name[0][1]) + ' ' + each_val['values']
                                else:
                                    product_dict['name'] = 'Full Mouth'
                                product_dict['quantity'] = 1
                                product_dict['price_unit'] = p_brw.lst_price
                                acc_obj = self.env['account.account'].search(
                                    [('name', '=', 'Local Sales'), ('account_type', '=', 'Income')], limit=1)
                                for account_id in jr_brw:
                                    # product_dict['account_id'] = account_id.payment_debit_account_id.id if account_id.payment_debit_account_id else acc_obj.id
                                    '''
                                        V15 payment_debit_account_id Field is deprecated. Currently adding Default account. This need to be fixed later
                                        with new v15 build features.
                                    '''
                                    product_dict['account_id'] = account_id.default_account_id.id if account_id.default_account_id else acc_obj.id
                                each_line.append(product_dict)
                                invoice_line_vals.append(each_line)
                            # Creating invoice dictionary
                            # invoice_vals['account_id'] = partner_brw.property_account_receivable_id.id
                            if patient_brw.current_insurance:
                                invoice_vals['partner_id'] = patient_brw.current_insurance.company_id.id
                            else:
                                invoice_vals['partner_id'] = partner_brw.id
                            invoice_vals['patient_id'] = partner_brw.id
                            # invoice_vals['partner_id'] = partner_brw.id
                            if current_physician:
                                invoice_vals['dentist'] = physician[0].id
                            invoice_vals['move_type'] = 'out_invoice'
                            invoice_vals['insurance_company'] = patient_brw.current_insurance.company_id.id
                            # invoice_vals['invoice_line_ids'] = invoice_line_vals              
                            
            if invoice_vals:
                pass