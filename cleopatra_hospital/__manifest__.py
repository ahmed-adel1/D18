{
    'name': "Cleopatra Hospital",

    'summary': "Module to manage all operations in hospitals",

    'description': """
    Featerus :
    1- Manage patients 
    2- manage doctors & nurses 
    """,

    'author': "Hisham",
    'website': "https://www.hisham.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'health',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',

        'views/patient_view.xml',
        'views/appointment_view.xml',
        'views/medicine_view.xml',
        'views/patient_tags_views.xml',

        'views/menus.xml',
        # ],
        # only loaded in demonstration mode
        # 'demo': [
        #     'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
