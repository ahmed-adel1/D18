from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


class Medicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'Medicine'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string = 'Name', readonly=False, store=True)

