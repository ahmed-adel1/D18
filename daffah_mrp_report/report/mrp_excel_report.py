from odoo import http
from odoo.http import request
import io
import xlsxwriter



class MrpExcelReport(http.Controller):
    @http.route('/report/mrp/production/excel/<int:production_id>', type='http', auth='user')
    def download_excel(self, production_id, **kwargs):
        record = request.env['mrp.production'].browse(production_id)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Manufacturing Order')

        headers = ['Projects_x', 'Product', 'Quantity', 'Bill of Material', 'Scheduled Date']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        sheet.write(1, 0, record.projects_x.name if record.projects_x else '')
        sheet.write(1, 1, record.product_id.name)
        sheet.write(1, 2, record.product_qty)
        sheet.write(1, 3, record.bom_id.display_name or '')
        sheet.write(1, 4, record.date_start)

        workbook.close()
        output.seek(0)

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Disposition', f'attachment; filename="mrp_order_{record.name}.xlsx"'),
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            ]
        )
