from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class AppointmentLine(models.Model):
    _name = 'appointment.line'


    appointment_id = fields.Many2one('hospital.appointment', string = 'Appointment')
    medicine_id = fields.Many2one('hospital.medicine', string = 'Medicine')
    dose = fields.Integer(pstring = "Dose")
