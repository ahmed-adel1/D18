from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class Doctor(models.Model):
    _name = 'hospital.doctor'

    name = fields.Char(string = 'Name', readonly=False, store=True)
