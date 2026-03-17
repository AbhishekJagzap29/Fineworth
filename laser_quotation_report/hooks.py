from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Populate default tech specs on existing quotations so the tab is not empty."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    orders = env["sale.order"].search([])
    for order in orders:
        if not order.tech_spec_ids:
            order.write({"tech_spec_ids": order._default_tech_specs()})
        if not order.plasma_spec_ids:
            order.write({"plasma_spec_ids": order._default_plasma_specs()})
        if not getattr(order, "optional_spec_ids", False) or not order.optional_spec_ids:
            order.write({"optional_spec_ids": order._default_optional_specs()})
        if not order.basic_price:
            order.basic_price = 2150000.0
