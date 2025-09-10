from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
from dateutil import relativedelta
import re


class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char(string='Name', required=True, tracking=True)
    reference = fields.Char(string='Patient Reference', readonly=True, copy=False, default='New')
    age = fields.Integer(string="Age", tracking=True, compute='_compute_age', store=True)
    date_of_birth = fields.Date(string='Date of Birth', required=True, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True, tracking=True)
    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-')
    ], string='Blood Group')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status')

    # Contact Information
    phone_number = fields.Char(string='Phone Number', required=True)
    emergency_contact = fields.Char(string='Emergency Contact')
    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.company.country_id)
    zip = fields.Char(string='ZIP Code')

    # Medical Information
    weight = fields.Float(string='Weight (kg)')
    height = fields.Float(string='Height (cm)')
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)
    allergies = fields.Text(string='Allergies')
    chronic_diseases = fields.Text(string='Chronic Diseases')
    current_medications = fields.Text(string='Current Medications')
    medical_history = fields.Text(string='Medical History')

    # Insurance Information
    insurance_company = fields.Char(string='Insurance Company')
    insurance_policy_number = fields.Char(string='Policy Number')
    insurance_validity = fields.Date(string='Insurance Valid Until')
    insurance_active = fields.Boolean(string='Insurance Active', compute='_compute_insurance_active', store=True)

    # Professional Information
    occupation = fields.Char(string='Occupation')
    employer = fields.Char(string='Employer')

    # System Fields
    state = fields.Selection([

        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(string='Patient Photo')

    # Related Fields
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')
    last_appointment_date = fields.Date(string='Last Appointment', compute='_compute_last_appointment')
    next_appointment_date = fields.Date(string='Next Appointment', compute='_compute_next_appointment')

    # Registration Information
    registration_date = fields.Date(string='Registration Date', default=fields.Date.today, readonly=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Primary Doctor')
    notes = fields.Text(string='Internal Notes')

    # Tags
    tag_ids = fields.Many2many('hospital.patient.tag', string='Tags')

    # Priority
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='0')

    # Computed Display Fields
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    is_birthday_today = fields.Boolean(string='Birthday Today', compute='_compute_is_birthday')

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or 'New'
        return super(Patient, self).create(vals)

    @api.depends('name', 'reference')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.reference}] {record.name}" if record.reference else record.name

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                age = today.year - record.date_of_birth.year
                if today.month < record.date_of_birth.month or \
                        (today.month == record.date_of_birth.month and today.day < record.date_of_birth.day):
                    age -= 1
                record.age = age
            else:
                record.age = 0

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight:
                height_m = record.height / 100
                record.bmi = round(record.weight / (height_m ** 2), 2)
            else:
                record.bmi = 0

    @api.depends('insurance_validity')
    def _compute_insurance_active(self):
        today = fields.Date.today()
        for record in self:
            record.insurance_active = bool(record.insurance_validity and record.insurance_validity > today)

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    @api.depends('appointment_ids.appointment_date')
    def _compute_last_appointment(self):
        today = fields.Date.today()
        for record in self:
            past_appointments = record.appointment_ids.filtered(
                lambda a: a.appointment_date and a.appointment_date <= today
            ).sorted('appointment_date', reverse=True)
            record.last_appointment_date = past_appointments[0].appointment_date if past_appointments else False

    @api.depends('appointment_ids.appointment_date')
    def _compute_next_appointment(self):
        today = fields.Date.today()
        for record in self:
            future_appointments = record.appointment_ids.filtered(
                lambda a: a.appointment_date and a.appointment_date > today
            ).sorted('appointment_date')
            record.next_appointment_date = future_appointments[0].appointment_date if future_appointments else False

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        today = date.today()
        for record in self:
            if record.date_of_birth:
                record.is_birthday_today = (record.date_of_birth.day == today.day and
                                            record.date_of_birth.month == today.month)
            else:
                record.is_birthday_today = False

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for record in self:
            if record.date_of_birth and record.date_of_birth > fields.Date.today():
                raise ValidationError(_("Date of birth cannot be in the future!"))

    @api.constrains('phone_number')
    def _check_phone_number(self):
        for record in self:
            if record.phone_number:
                # Basic phone validation - adjust regex as needed
                if not re.match(r'^[0-9+\-\s\(\)]+$', record.phone_number):
                    raise ValidationError(_("Please enter a valid phone number!"))

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError(_("Please enter a valid email address!"))

    @api.constrains('weight', 'height')
    def _check_measurements(self):
        for record in self:
            if record.weight and record.weight <= 0:
                raise ValidationError(_("Weight must be greater than 0!"))
            if record.height and record.height <= 0:
                raise ValidationError(_("Height must be greater than 0!"))

    @api.onchange('country_id')
    def _onchange_country(self):
        if self.country_id and self.state_id and self.state_id.country_id != self.country_id:
            self.state_id = False

    def action_register(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'registered'
                # Send welcome email or notification
                self._send_welcome_notification()

    def action_activate(self):
        for record in self:
            if record.state in ['registered', 'inactive']:
                record.state = 'active'

    def action_deactivate(self):
        for record in self:
            if record.state == 'active':
                record.state = 'inactive'

    def action_archive(self):
        for record in self:
            record.state = 'archived'
            record.active = False

    def action_print_patient_card(self):
        # Return action to print patient card report
        return self.env.ref('hospital.action_report_patient_card').report_action(self)

    def action_send_sms(self):
        # Placeholder for SMS functionality
        raise UserError(_("SMS functionality is not configured yet!"))

    def action_send_email(self):
        # Open email compose wizard
        template = self.env.ref('hospital.email_template_patient_general', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = {
            'default_model': 'hospital.patient',
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Appointments'),
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def _send_welcome_notification(self):
        # Send notification when patient is registered
        for record in self:
            record.message_post(
                body=_("Welcome %s! Your registration is complete. Your patient reference is %s") %
                     (record.name, record.reference),
                subject=_("Registration Successful"),
                message_type='notification',
            )

    @api.model
    def get_birthday_patients(self):
        """Get patients with birthday today - useful for cron job"""
        today = date.today()
        patients = self.search([])
        birthday_patients = patients.filtered(lambda p: p.is_birthday_today)
        return birthday_patients

    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'archived']:
                raise UserError(_("You can only delete patients in 'Draft' or 'Archived' state!"))
        return super(Patient, self).unlink()


