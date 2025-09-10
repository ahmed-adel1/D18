from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


class Appointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    reference = fields.Char(string='Reference')
    patient_name = fields.Char(string='Patient Name')
    appointment_date = fields.Datetime(string='Date')

    doctor_id = fields.Many2one('hospital.doctor', string='Primary Doctor')
    
    patient_id = fields.Many2one('hospital.patient', string = 'Patient')

    line_ids = fields.One2many('appointment.line', 'appointment_id', string="", copy=False)


    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('not_shown', 'Not Shown'),
            ('cancel', 'Cancelled')
        ],
        string="Status",  tracking=True, default='draft')


    notes = fields.Text(string = "Notes")



    def action_print_new_appointment(self):
        print ("new appointment")
