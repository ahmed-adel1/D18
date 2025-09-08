from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_delivery_deadline = fields.Date(string='Delivery Deadline')
    x_sales_coordinator_id  = fields.Many2one(
    'res.users',
    string='Sales Coordinator',
        # domain="[('groups_id', 'name', 'Sales / User')]"
    )

    @api.constrains('x_delivery_deadline', 'date_order')
    def _check_delivery_deadline(self):
        for order in self:
            if order.x_delivery_deadline and order.date_order:
                if order.x_delivery_deadline < order.date_order.date():
                    raise UserError('Delivery Deadline must not be earlier than Order Date.')

    def action_confirm(self):
        for order in self:
            if not order.order_line:
                raise UserError('You cannot confirm a Sales Order without any order lines.')
            if not order.x_delivery_deadline:
                raise UserError('Delivery Deadline must be set before confirming the order.')
        return super(SaleOrder, self).action_confirm()

    def write(self, vals):
        if 'x_sales_coordinator_id' in vals:
            for order in self:
                if order.state != 'draft':
                    user = self.env.user
                    if not user.has_group('sales_team.group_sale_manager'):
                        raise UserError('Only Sales Managers can edit the Sales Coordinator after confirmation.')
        return super(SaleOrder, self).write(vals)
