# -*- coding: utf-8 -*-
{
    'name': "od_openacademy",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Odoo Discussions",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail'],
    'assets': {
        'web.assets_backend': [
            'od_openacademy/static/src/css/style.css',
        ],
        'web.report_assets_common': [
            '/od_openacademy/static/src/css/fonts.css',
        ]
    },

    # always loaded
    'data': [
        'data/course_tags.xml',
        'security/security_groups.xml',
        'security/access_control_lists.xml',
        'security/record_rules.xml',
        'data/ir_sequence.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_partner.xml',
        'reports/custom_header.xml',
        'reports/reports.xml',
        'reports/duplicate_course_report.xml',
        'views/tracking_session_values.xml',
        'views/res_config_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
