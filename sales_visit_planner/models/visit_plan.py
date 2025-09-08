from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError
from datetime import datetime


class VisitPlan(models.Model):
    _name = 'visit.plan'
    _description = 'Sales Visit Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def send_daily_reminder(self):
        today = datetime.today()
        visits_today = self.search([
            ('visit_date', '>=', today.replace(hour=0, minute=0, second=0)),
            ('visit_date', '<', today.replace(hour=23, minute=59, second=59))
        ])
        template = self.env.ref('sales_visit_planner.email_template_daily_visits')
        for visit in visits_today:
            template.send_mail(visit.id, force_send=True)

    name = fields.Char(string="Visit Title", required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True, tracking=True)
    salesperson_id = fields.Many2one('res.users', string="Salesperson",
                                     default=lambda self: self.env.user,
                                     tracking=True)
    visit_date = fields.Datetime(string="Visit Date", required=True, tracking=True)
    purpose = fields.Selection([
        ('prospecting', 'Prospecting'),
        ('followup', 'Follow Up'),
        ('support', 'Support'),
        ('collection', 'Collection'),
    ], string="Purpose", tracking=True)
    notes = fields.Text(string="Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string="Status", default='draft', tracking=True)
    reason_reset_draft = fields.Text(
        string="Reset Reason",
        readonly=True,  # ممنوع يتعدل عادي
        copy=False
    )

    is_overdue = fields.Boolean(string="Overdue", compute='_compute_is_overdue', store=True)
    duration_planned = fields.Float(string="Planned Duration (Hours)")
    duration_effective = fields.Float(string="Effective Duration (Hours)")
    visit_outcome = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('fail', 'Fail')
    ], string="Outcome")
    next_step = fields.Text(string="Next Step")
    lead_id = fields.Many2one('crm.lead', string="Related Lead")
    reference = fields.Char(string="Reference", required=True, copy=False, readonly=True, default=lambda self: "New")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("sales.visit.plan") or "New"
        return super().create(vals_list)

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.reason_reset_draft = False

    def action_schedule(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'scheduled'

    def action_done(self):
        for rec in self:
            if rec.state == 'scheduled':
                rec.state = 'done'

    # def action_cancel(self):
    #     for rec in self:
    #         if rec.state not in ('done', 'cancel'):
    #             rec.state = 'cancel'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'scheduled':
                continue  # تجاهل
            if rec.state not in ('done', 'cancel'):
                rec.state = 'cancel'


    # def action_open_reset_draft_wizard(self):
    #     return {
    #         'name': 'Reason to Reset to Draft',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'reset.draft.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'active_id': self.id},
    #     }
    def action_cancel(self):
        return {
            'name': 'Cancel Visit',
            'type': 'ir.actions.act_window',
            'res_model': 'visit.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.constrains('visit_date', 'duration_planned', 'salesperson_id', 'state')
    def _check_schedule_conflict(self):
        for visit in self:
            if visit.state != 'scheduled':
                continue
            # مدة الزيارة الافتراضية ساعة لو مفيش duration_planned
            duration = visit.duration_planned or 1.0
            start = visit.visit_date
            end = start + timedelta(hours=duration)
            # البحث عن زيارات متداخلة لنفس المندوب
            conflicting = self.search([
                ('id', '!=', visit.id),
                ('salesperson_id', '=', visit.salesperson_id.id),
                ('state', '=', 'scheduled'),
                ('visit_date', '<', end),
                ('visit_date', '>', start - timedelta(hours=duration))
            ])
            if conflicting:
                raise UserError(f"Conflict with visit: {conflicting[0].name} at {conflicting[0].visit_date}")

    @api.constrains('partner_id', 'visit_date')
    def _check_partner_and_date(self):
        for record in self:
            if not record.partner_id or not record.visit_date:
                raise ValidationError("Customer and Visit Date are required.")

    @api.depends('visit_date', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_overdue = record.state not in ['done', 'cancel'] and record.visit_date < now

    # Buttons
    def action_schedule(self):
        for record in self:
            record.state = 'scheduled'
            # Create activity
            if record.partner_id:
                self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'res_id': record.partner_id.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'user_id': record.salesperson_id.id,
                    'date_deadline': record.visit_date,
                    'summary': f"Sales Visit: {record.name}"
                })

    def action_mark_done(self):
        for record in self:
            if not record.visit_outcome or not record.next_step:
                raise ValidationError("Outcome and Next Step are required to mark as Done.")
            record.state = 'done'
            # Create follow-up activity after 3 days
            if record.partner_id:
                self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'res_id': record.partner_id.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'user_id': record.salesperson_id.id,
                    'date_deadline': fields.Datetime.to_string(
                        fields.Datetime.from_string(record.visit_date) + timedelta(days=3)),
                    'summary': f"Follow-up: {record.next_step}"
                })

    @api.onchange('lead_id')
    def _onchange_lead(self):
        if self.lead_id and not self.partner_id:
            self.partner_id = self.lead_id.partner_id


@api.depends('visit_date', 'state')
def _compute_is_overdue(self):
    now = fields.Datetime.now()
    for record in self:
        record.is_overdue = record.state not in ['done', 'cancel'] and record.visit_date and record.visit_date < now


@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    for record in records:
        record._check_conflict()
    return records


def write(self, vals):
    res = super().write(vals)
    self._check_conflict()
    return res


def _check_conflict(self):
    for record in self:
        if record.state == 'scheduled':
            start = record.visit_date
            end = start + timedelta(hours=record.duration_planned or 1.0)
            domain = [
                ('id', '!=', record.id),
                ('salesperson_id', '=', record.salesperson_id.id),
                ('state', '=', 'scheduled'),
                ('visit_date', '<', end),
            ]
            conflicts = self.search(domain)
            for conf in conflicts:
                conf_end = conf.visit_date + timedelta(hours=conf.duration_planned or 1.0)
                if conf.visit_date < end and start < conf_end:
                    raise ValidationError(
                        f"Conflict detected with visit '{conf.name}' for {conf.salesperson_id.name} at {conf.visit_date}."
                    )
