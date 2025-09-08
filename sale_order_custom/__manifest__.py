{
    'name': 'Sales Order Customizations',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Add delivery deadline and sales coordinator fields with validations',
    'author': 'Your Name',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
