{
    'name': 'MO Excel Export',
    'version': '1.0',
    'summary': 'Export multiple Manufacturing Orders to Excel',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mo_excel_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
