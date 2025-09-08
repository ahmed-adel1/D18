from odoo import api, SUPERUSER_ID

def create_email_templates(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['sale.order']._create_email_template()


