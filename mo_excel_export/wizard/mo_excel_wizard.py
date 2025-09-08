# from odoo import models, fields
# import io
# import xlsxwriter
# import base64
#
#
# class MoExcelExportWizard(models.TransientModel):
#     _name = 'mo.excel.export.wizard'
#     _description = 'Export Manufacturing Orders to Excel'
#
#     mo_ids = fields.Many2many('mrp.production', string="Manufacturing Orders")
#     file_data = fields.Binary('File', readonly=True)
#     file_name = fields.Char('File Name', readonly=True)
#
#     def action_export_excel(self):
#         import io
#         import xlsxwriter
#         import base64
#
#         all_components = sorted({
#             move.product_id.display_name
#             for mo in self.mo_ids
#             for move in mo.move_raw_ids
#         })
#
#         output = io.BytesIO()
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         sheet = workbook.add_worksheet('Manufacturing Orders')
#
#         header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
#         cell_fmt = workbook.add_format({'border': 1})
#
#         headers = ['Scheduled Date', 'Reference', 'Destination Location',
#                    'Responsible', 'Product', 'Quantity', 'UoM'] + all_components
#         for col, head in enumerate(headers):
#             sheet.write(0, col, head, header_fmt)
#
#         row = 1
#         for mo in self.mo_ids:
#             sheet.write(row, 0, str(mo.date_start or ''), cell_fmt)
#             sheet.write(row, 1, mo.name or '', cell_fmt)
#             sheet.write(row, 2, mo.location_dest_id.display_name or '', cell_fmt)
#             sheet.write(row, 3, mo.user_id.name or '', cell_fmt)
#             sheet.write(row, 4, mo.product_id.display_name or '', cell_fmt)
#             sheet.write(row, 5, mo.product_qty or 0, cell_fmt)
#             sheet.write(row, 6, mo.product_uom_id.name or '', cell_fmt)
#
#             comp_map = {m.product_id.display_name: m.product_uom_qty for m in mo.move_raw_ids}
#             for i, comp in enumerate(all_components, start=7):
#                 sheet.write(row, i, comp_map.get(comp, 0), cell_fmt)
#             row += 1
#
#         workbook.close()
#         file_data = base64.b64encode(output.getvalue())
#         output.close()
#
#         self.write({
#             'file_data': file_data,
#             'file_name': 'manufacturing_orders.xlsx'
#         })
#
#
#         return { لو عاوزه يفتح من wizard
#             'type': 'ir.actions.act_window',
# #             'res_model': 'mo.excel.export.wizard',
#             'view_mode': 'form',
#             'res_id': self.id,
#             'target': 'new',
#         }
from odoo import models, fields
import io
import xlsxwriter
import base64


class MoExcelExportWizard(models.TransientModel):
    _name = 'mo.excel.export.wizard'
    _description = 'Export Manufacturing Orders to Excel'

    mo_ids = fields.Many2many('mrp.production', string="Manufacturing Orders")
    file_data = fields.Binary('File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)

    def action_export_excel(self):
        all_components = sorted({
            move.product_id.display_name
            for mo in self.mo_ids
            for move in mo.move_raw_ids
        })

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Manufacturing Orders')

        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
        cell_fmt = workbook.add_format({'border': 1})

        headers = ['Project','projects_x','Reference', 'Scheduled Date',
                   'Responsible', 'Product', 'Quantity', 'UoM','company_daffah'] + all_components
        for col, head in enumerate(headers):
            sheet.write(0, col, head, header_fmt)

        row = 1
        for mo in self.mo_ids:
            sheet.write(row, 0, mo.project_id.name or '', cell_fmt)  # Project
            sheet.write(row, 1, mo.projects_x.name or '', cell_fmt)  # projects_x (لو موجود في الموديل)
            sheet.write(row, 2, mo.name or '', cell_fmt)  # Reference
            sheet.write(row, 3, str(mo.date_start or ''), cell_fmt)  # Scheduled Date
            sheet.write(row, 4, mo.user_id.name or '', cell_fmt)  # Responsible
            sheet.write(row, 5, mo.product_id.display_name or '', cell_fmt)  # Product
            sheet.write(row, 6, mo.product_qty or 0, cell_fmt)  # Quantity
            sheet.write(row, 7, mo.product_uom_id.name or '', cell_fmt)  # UoM
            sheet.write(row, 8, mo.company_daffah or '', cell_fmt)  # company_daffah

            comp_map = {m.product_id.display_name: m.product_uom_qty for m in mo.move_raw_ids}
            for i, comp in enumerate(all_components, start=7):
                sheet.write(row, i, comp_map.get(comp, 0), cell_fmt)
            row += 1

            workbook.close()
        file_data = base64.b64encode(output.getvalue())
        output.close()

        # نحفظ الملف في السجل (لو حابب) عشان تبقى موجودة بس مش ضروري
        self.write({
            'file_data': file_data,
            'file_name': 'manufacturing_orders.xlsx'
        })

        # نرجع رابط تحميل الملف مباشرة
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file_data/{self.file_name}?download=true',
            'target': 'self',
        }

