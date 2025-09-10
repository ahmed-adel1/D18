from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta

class PatientTag(models.Model):
    _name = 'hospital.patient.tag'
    _description = 'Patient Tag'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!')
    ]







