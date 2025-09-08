{
    'name': 'Sales Visit Planner',
    'version': '1.0',
    'summary': 'Manage sales representatives client visits',
    'sequence': -100,
    'description': """
        Manage sales representatives client visits:
        schedule, execute, record outcomes, and generate reports.
    """,
    'category': 'Sales',
    'author': 'Zaki Dev',
    'website': 'https://example.com',
    'depends': ['base', 'sale', 'mail'],
    'data': [
        'report/visit_plan_report.xml',
        'report/visit_plan_report_template.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu_views.xml',
        'views/visit_plan_views.xml',
        'data/demo.xml',
        'data/cron_daily_visits.xml',
        'data/email_template_daily.xml',
    ],
    'demo': ['data/demo.xml'],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
