{
    'name': 'Laser Machine Quotation Report',
    'version': '1.0',
    'summary': 'Custom quotation format for machine quotation',
    'author': 'Your Name',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'report/quotation_template.xml',
        'report/quotation_template_powermax125.xml',
        'report/report_action.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
