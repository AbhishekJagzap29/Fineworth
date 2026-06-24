{
    'name': 'Laser Machine Quotation Report',
    'version': '1.0',
    'summary': 'Custom quotation format for machine quotation',
    'author': 'Your Name',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/plasma_tax_option_data.xml',
        'views/sale_order_view.xml',
        'data/mail_template_data.xml',
        'report/laser_quotation.xml',
        'report/Plasma_quotation.xml',
        'report/report_action.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
