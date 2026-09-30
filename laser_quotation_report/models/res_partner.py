from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("name")
    def _check_unique_customer_name(self):
        for partner in self:
            if not partner.name or not partner.name.strip():
                continue
            clean_name = partner.name.strip()
            domain = [
                ("name", "=ilike", clean_name),
                ("id", "!=", partner.id),
            ]
            existing = self.search(domain, limit=1)
            if existing:
                raise ValidationError(
                    _(
                        "A customer with the name '%s' already exists. "
                        "Duplicate customer names are not allowed.",
                        partner.name,
                    )
                )
