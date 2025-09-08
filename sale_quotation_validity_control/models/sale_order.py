from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from datetime import timedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    validity_days = fields.Integer(
        string="Validity (days)",
        default=2,
        help="Number of days the quotation remains valid from its creation/order date.",
    )

    expires_on = fields.Date(
        string="Expires On",
        compute="_compute_expires_on",
        store=True,
        help="Order Date + validity days.",
    )

    is_expired = fields.Boolean(
        string="Is Expired",
        compute="_compute_is_expired",
        help="True if today is after expiry and record is still a quotation (draft/sent).",
        store=True
    )

    override_expiry = fields.Boolean(
        string="Supervisor Override",
        default=False,
        help="Sales Supervisor can enable this to bypass expiry.",
    )

    @api.depends("validity_days", "date_order")
    def _compute_expires_on(self):
        for order in self:
            base_date = fields.Date.to_date(order.date_order) if order.date_order else fields.Date.context_today(order)
            order.expires_on = base_date + timedelta(days=order.validity_days or 0)

    @api.depends("expires_on", "state")
    def _compute_is_expired(self):
        today = fields.Date.context_today(self)
        for order in self:
            order.is_expired = bool(
                order.expires_on
                and today > order.expires_on
                and order.state in ("draft", "sent")
            )

    def write(self, vals):
        # Only Sales Supervisors can enable override
        if "override_expiry" in vals and vals.get("override_expiry"):
            if not self.env.user.has_group("sale_quotation_validity_control.group_sale_supervisor"):
                raise AccessError(_("Only Sales Supervisors can enable expiry override."))
        return super().write(vals)

    def action_confirm(self):
        for order in self:
            if order.state in ("draft", "sent") and order.is_expired:
                if not order.override_expiry:
                    raise UserError(
                        _("Quotation is expired. Cannot confirm unless override is set by Sales Supervisor."))
                else:
                    order.message_post(body=_("Expired quotation confirmed by Supervisor override"))
        return super().action_confirm()

    @api.model
    def cron_send_expiry_reminders(self):
        today = fields.Date.context_today(self)
        reminder_date = today + timedelta(days=2)
        quotes = self.search([("state", "in", ("draft", "sent")), ("expires_on", "=", reminder_date)])
        template = self.env.ref("sale_quotation_validity_control.email_template_quotation_expiry_reminder",
                                raise_if_not_found=False)
        for quote in quotes:
            if template:
                template.send_mail(quote.id, force_send=True)
            quote.message_post(body=_("Expiry reminder sent"))

    @api.model
    def _create_email_template(self):
        """Create Email Template automatically if not exists."""
        existing = self.env['mail.template'].search([('name', '=', 'Quotation Expiry Reminder')], limit=1)
        if not existing:
            self.env['mail.template'].create({
                'name': 'Quotation Expiry Reminder',
                'model_id': self.env.ref('sale.model_sale_order').id,
                'email_from': "${object.company_id.email or ''}",
                'subject': "Quotation ${object.name} Expiry Reminder",
                'body_html': """
                    <p>Hello ${object.partner_id.name},</p>
                    <p>Your quotation <strong>${object.name}</strong> will expire on 
                    <strong>${object.expires_on}</strong>.</p>
                    <p>Link: <a href="${object.get_portal_url()}">${object.name}</a></p>
                    <p>Salesperson: ${object.user_id.name}</p>
                """,

            })
