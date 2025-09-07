from odoo import models, fields, api
from odoo.exceptions import UserError


class VisitCancelWizard(models.TransientModel):
    _name = 'visit.cancel.wizard'
    _description = 'Cancel Visit Wizard'

    notes = fields.Text(string="Notes")

    def action_confirm(self):
        # جلب الزيارة اللي اتعمل عليها العملية
        active_id = self.env.context.get('active_id')
        visit = self.env['visit.plan'].browse(active_id)
        # تحديث الحالة وكتابة السبب
        visit.write({
            'state': 'cancel',
            'cancel': self.reason,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

# def action_confirm(self):
#     active_id = self.env.context.get('active_id')
#     visit = self.env['visit.plan'].browse(active_id)
#     visit.write({
#         'state': 'cancel',
#         'cancel_reason': self.reason
#     })
#     return {'type': 'ir.actions.client', 'tag': 'reload'}

    # reason = fields.Text(string="Cancel Reason", required=True)
    #
    # def action_confirm_cancel(self):
    #     active_id = self.env.context.get('active_id')
    #     visit = self.env['visit.plan'].browse(active_id)
    #     if not visit:
    #         raise UserError("الزيارة مش موجودة")
    #     visit.write({
    #         'state': 'cancel',
    #         'notes': (visit.notes or '') + "\nCancel Reason: " + self.reason
    #     })
    #


