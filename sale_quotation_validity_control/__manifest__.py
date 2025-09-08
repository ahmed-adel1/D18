{
    "name": "Sale Quotation Validity Controls",
    "version": "18.0.1.0.0",
    "summary": "Stage1 - Adds validity fields and UI for sale quotations (Odoo 18 Community).",
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": ["base", "sale", "mail"],
    'post_init_hook': 'create_email_templates',
    "data": [
        'security/sale_supervisor_group.xml',
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        # 'data/demo_quotation.xml',
    ],
    'demo': [
        'data/demo_quotation.xml',
    ],

    "installable": True,
    "application": False,
}
