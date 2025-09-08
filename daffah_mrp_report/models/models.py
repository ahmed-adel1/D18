from odoo import models, fields, api


class MrpReport(models.Model):
    _inherit = 'mrp.production'

    company_daffah = fields.Char()
    projects_x = fields.Many2one(
        comodel_name='project.project',
        string='Projects_x',
        required=False)


    def mrp_excel_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/mrp/production/excel/{self.id}',
            'target': 'new',
        }
