# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from mock import DEFAULT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import hashlib
import time


class DoctorSlot(models.Model):
    _name = 'doctor.slot'
    _description = 'Doctor Slot'

    doctor_id = fields.Many2one('medical.physician', string='Doctor')
    weekday = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Week Day', required=True)
    start_hour = fields.Float('Starting Hour')
    end_hour = fields.Float('Ending Hour')

    @api.model
    def get_doctors_slot(self, target_date=False, doctor=False):
        if target_date:
            ask_time = datetime.strptime(target_date, "%a %b %d %Y %H:%M:%S %Z%z").date()
            weekday = ask_time.isoweekday()
        else:
            weekday = datetime.today().isoweekday()

        domain = [('weekday', '=', str(weekday))]
        if doctor:
            domain += [('doctor_id', '=', int(doctor))]
        slot_ids = sorted(self.search(domain), reverse=True)
        data_dict = {}
        for lt in slot_ids:
            doctor_id = lt.doctor_id
            start_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.start_hour * 60, 60))
            end_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.end_hour * 60, 60))
            if doctor_id.id not in data_dict:
                data_dict[doctor_id.id] = {
                    'id': doctor_id.id,
                    'name': doctor_id.res_partner_medical_physician_id.name,
                    'count': 1,
                    'time_slots': [{'start_hour': start_hour, 'end_hour': end_hour}]
                }
            else:
                data_dict[doctor_id.id]['count'] += 1
                data_dict[doctor_id.id]['time_slots'].append({'start_hour': start_hour, 'end_hour': end_hour})

        final_list = []
        for i in data_dict:
            final_list.append(data_dict.get(i))
        return final_list

    @api.model
    def get_doctors_slot_validation(self, target_date=False, doctor=False):
        is_available_slot = False
        if target_date:
            ask_time = datetime.strptime(target_date, "%a %b %d %Y %H:%M:%S %Z%z").date()
            weekday = ask_time.isoweekday()
        else:
            weekday = datetime.today().isoweekday()
        domain = [('weekday', '=', str(weekday))]
        if doctor:
            domain += [('doctor_id', '=', int(doctor))]
        slot_ids = sorted(self.search(domain), reverse=True)
        for lt in slot_ids:
            start_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.start_hour * 60, 60))
            end_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.end_hour * 60, 60))
            ask_time = datetime.strptime(target_date, "%a %b %d %Y %H:%M:%S %Z%z").date()

            start_time = datetime.strptime(start_hour, '%H:%M').time()
            start_date_time = datetime.combine(ask_time, start_time)

            end_time = datetime.strptime(end_hour, '%H:%M').time()
            end_date_time = datetime.combine(ask_time, end_time)

            if self.env.context.get('dateToString') and self.env.context.get('from_time'):
                str_date = datetime.strptime(self.env.context.get('dateToString'), "%a %b %d %Y %H:%M:%S %Z%z").date()
                str_date = str(str_date) + ' ' + self.env.context.get('from_time')
                datetime_object = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
                if datetime_object>=start_date_time and datetime_object<=end_date_time:
                    is_available_slot = True
        return is_available_slot