from odoo import _, api, fields, models
from odoo.exceptions import UserError
import json
from lxml import etree


# Default rows for the technical specification table on quotations
TECH_SPEC_DEFAULTS = [
    ("Effective Cutting width X axis", "2500 mm"),
    ("Effective Cutting length Y axis", "6500 mm"),
    ("Laser power sources", "6000 watts"),
    ("Laser power sources name", "Raycus"),
    ("Laser torch head", "WSX"),
    ("Controller type", "Computer numeric control"),
    ("Controller name", "Aheadtech Raytools software"),
    ("AC servo digital drive package", "YASAKA"),
    ("Planetary gearbox", "REDOVAC"),
    ("Drag chain for axis", "Kableschepp"),
    ("Professional valve assembly", "SMC"),
    ("Ethernet communication", "Available"),
    ("LM Guide ways", "Hiwin"),
    ("Chiller for laser power sources", "HANLEE"),
    ("Panel cooler for control panel", "Empee"),
]


# Default rows for the plasma specification table on quotations
PLASMA_SPEC_DEFAULTS = [
    ("Effective Travel Cutting width X axis", "1500 mm"),
    ("Effective Travel Cutting length Y axis", "9000 mm"),
    ("No of plasma cutting torch", "1 Nos"),
    ("No of flame cutting torch", "1 Nos"),
    ("Maximum piercing capacity for flame cutting torch", "50 mm"),
    ("Minimum cutting thickness for flame cutting torch", "3 mm"),
    ("Maximum cutting thickness for flame cutting torch", "150 mm"),
    ("Hypertherm Plasma power source (Powermax 125) with Plasma height control", "1 Nos"),
    ("Maximum piercing capacity for plasma cutting torch M.S", "25 mm"),
    ("Minimum cutting thickness for plasma cutting torch M.S", "1 mm"),
    ("Maximum piercing capacity for plasma cutting torch S.S", "20 mm"),
    ("Minimum cutting thickness for plasma cutting torch S.S", "1 mm"),
    ("Controller type", "Computer numeric control"),
    ("Controller name", "YASAKA"),
    ("Controller model", "Power P 10\" Display"),
    ("Display size", "10 Inch Color"),
    ("Drag chain for axis", "kableslapp"),
    ("Positioning speed", "12 m/min"),
    ("Drag chain for axis", "kable schepp"),
]

# Default rows for optional add-ons on quotations
OPTIONAL_SPEC_DEFAULTS = [
    ("DUST COLLECTOR FOR MACHINE", "2,80,000.00"),
    ("UPS FOR MACHINE", "5,50,000.00"),
    ("COMPRESSOR 20 HP WITH DRYER WITH TANK", "4,80,000.00"),
]


class SaleOrderTechSpec(models.Model):
    _name = "sale.order.tech.spec"
    _description = "Sale Order Technical Specification"
    _order = "sequence, id"

    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        ondelete="cascade",
        required=True,
    )
    sequence = fields.Integer(string="Sr. No.", default=lambda self: self._default_sequence())
    name = fields.Char(string="Description", required=True)
    value = fields.Char(string="Technical Specification")

    @api.model
    def _default_sequence(self):
        """Return the next sequence number based on the active_id context."""
        if self.env.context.get("default_sequence"):
            return self.env.context["default_sequence"]
        order_id = self.env.context.get("default_order_id")
        if order_id:
            last = self.search(
                [("order_id", "=", order_id)],
                order="sequence desc, id desc",
                limit=1,
            )
            return (last.sequence + 1) if last else 1
        return 1

    def _default_name_from_sequence(self, seq):
        if 1 <= seq <= len(TECH_SPEC_DEFAULTS):
            return TECH_SPEC_DEFAULTS[seq - 1][0]
        return f"Item {seq}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("order_id") and not vals.get("sequence"):
                last_sequence = self.search(
                    [("order_id", "=", vals["order_id"])],
                    order="sequence desc, id desc",
                    limit=1,
                ).sequence
                vals["sequence"] = last_sequence + 1 if last_sequence else 1
            if not vals.get("name"):
                seq = vals.get("sequence") or 1
                vals["name"] = self._default_name_from_sequence(seq)
        return super().create(vals_list)

    def write(self, vals):
        vals = vals.copy()
        # Keep sequence managed by the system, but allow users to edit the description.
        if not self.env.context.get("allow_protected_fields"):
            vals.pop("sequence", None)
        return super().write(vals)


class SaleOrderPlasmaSpec(models.Model):
    _name = "sale.order.plasma.spec"
    _description = "Sale Order Plasma Specification"
    _order = "sequence, id"

    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        ondelete="cascade",
        required=True,
    )
    sequence = fields.Integer(string="Sr. No.", default=lambda self: self._default_sequence())
    name = fields.Char(string="Description", required=True)
    value = fields.Char(string="Technical Specification")

    @api.model
    def _default_sequence(self):
        """Return the next sequence number based on the active_id context."""
        if self.env.context.get("default_sequence"):
            return self.env.context["default_sequence"]
        order_id = self.env.context.get("default_order_id")
        if order_id:
            last = self.search(
                [("order_id", "=", order_id)],
                order="sequence desc, id desc",
                limit=1,
            )
            return (last.sequence + 1) if last else 1
        return 1

    def _default_name_from_sequence(self, seq):
        if 1 <= seq <= len(PLASMA_SPEC_DEFAULTS):
            return PLASMA_SPEC_DEFAULTS[seq - 1][0]
        return f"Item {seq}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("order_id") and not vals.get("sequence"):
                last_sequence = self.search(
                    [("order_id", "=", vals["order_id"])],
                    order="sequence desc, id desc",
                    limit=1,
                ).sequence
                vals["sequence"] = last_sequence + 1 if last_sequence else 1
            if not vals.get("name"):
                seq = vals.get("sequence") or 1
                vals["name"] = self._default_name_from_sequence(seq)
        return super().create(vals_list)

    def write(self, vals):
        vals = vals.copy()
        # Keep sequence managed by the system, but allow users to edit the description.
        if not self.env.context.get("allow_protected_fields"):
            vals.pop("sequence", None)
        return super().write(vals)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    quotation_type = fields.Selection(
        selection=[
            ("laser", "Laser Cutting"),
            ("plasma", "Plasma Cutting"),
        ],
        string="Quotation Type",
        required=True,
    )
    laser_power = fields.Integer(string="Laser Power (Watts)")
    basic_price = fields.Monetary(
        string="Basic Price",
        currency_field="currency_id",
        default=2150000.0,
        help="Base price for the Fine Worth profile cutting machine shown on the quotation.",
    )
    advance_percent = fields.Float(string="Advance %", default=40.0)
    gst_percent = fields.Float(string="GST %", default=18.0)
    balance_percent = fields.Float(string="Balance %", default=60.0)
    payment_term_name = fields.Char(
        string="Payment Terms",
        related="payment_term_id.name",
        readonly=True,
    )
    model_name = fields.Char(
            string="Machine Model",
            default="FINELASER3015"
    )
    
    
    offer_title = fields.Char(
        string="Offer Title",
        default="Offer for CNC Fiber Laser Cutting Machine 6000 WATTS",
        help="Heading text printed on the quotation PDF; leave blank to use the default",
    )
    tech_spec_ids = fields.One2many(
    comodel_name="sale.order.tech.spec",
    inverse_name="order_id",
    string="Technical Specifications",
    copy=True,
    default=lambda self: self._default_tech_specs(),
    )

    plasma_spec_ids = fields.One2many(
        comodel_name="sale.order.plasma.spec",
        inverse_name="order_id",
        string="Plasma Specifications",
        copy=True,
        default=lambda self: self._default_plasma_specs(),
    )

    optional_spec_ids = fields.One2many(
        comodel_name="sale.order.optional.spec",
        inverse_name="order_id",
        string="Optional Items",
        copy=True,
        default=lambda self: self._default_optional_specs(),
    )
    
    

    @api.model
    def _default_tech_specs(self):
        """Pre-fill the technical spec table with our standard rows."""
        return [
            (0, 0, {"sequence": idx + 1, "name": name, "value": value})
            for idx, (name, value) in enumerate(TECH_SPEC_DEFAULTS)
        ]

    @api.model
    def _default_plasma_specs(self):
        """Pre-fill the plasma spec table with our standard rows."""
        return [
            (0, 0, {"sequence": idx + 1, "name": name, "value": value})
            for idx, (name, value) in enumerate(PLASMA_SPEC_DEFAULTS)
        ]

    @api.model
    def _default_optional_specs(self):
        """Pre-fill the optional items table with the standard add-ons."""
        return [
            (0, 0, {"sequence": idx + 1, "name": name, "value": value})
            for idx, (name, value) in enumerate(OPTIONAL_SPEC_DEFAULTS)
        ]

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "tech_spec_ids" in fields_list and not res.get("tech_spec_ids"):
            res["tech_spec_ids"] = self._default_tech_specs()
        if "plasma_spec_ids" in fields_list and not res.get("plasma_spec_ids"):
            res["plasma_spec_ids"] = self._default_plasma_specs()
        if "optional_spec_ids" in fields_list and not res.get("optional_spec_ids"):
            res["optional_spec_ids"] = self._default_optional_specs()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("tech_spec_ids"):
                vals["tech_spec_ids"] = self._default_tech_specs()
            if not vals.get("plasma_spec_ids"):
                vals["plasma_spec_ids"] = self._default_plasma_specs()
            if not vals.get("optional_spec_ids"):
                vals["optional_spec_ids"] = self._default_optional_specs()
        orders = super().create(vals_list)
        orders._normalize_spec_lines()
        return orders

    def write(self, vals):
        res = super().write(vals)
        self._normalize_spec_lines()
        return res

    @api.onchange("tech_spec_ids", "tech_spec_ids.name", "tech_spec_ids.value")
    def _onchange_tech_spec_ids(self):
        for order in self:
            order._resequence_lines(order.tech_spec_ids)

    @api.onchange("plasma_spec_ids", "plasma_spec_ids.name", "plasma_spec_ids.value")
    def _onchange_plasma_spec_ids(self):
        for order in self:
            order._resequence_lines(order.plasma_spec_ids)

    def _resequence_lines(self, lines):
        for idx, line in enumerate(lines, start=1):
            line.sequence = idx

    def _normalize_spec_lines(self):
        """Keep specification line numbering tidy after add/remove operations."""
        for order in self:
            # Technical specs: resequence only, preserving user-entered descriptions.
            for idx, line in enumerate(order.tech_spec_ids.sorted("sequence")):
                line.with_context(allow_protected_fields=True).write({"sequence": idx + 1})

            # Plasma specs: resequence only, preserving user-entered descriptions.
            for idx, line in enumerate(order.plasma_spec_ids.sorted("sequence")):
                line.with_context(allow_protected_fields=True).write({"sequence": idx + 1})

            # Optional items: resequence and reset description labels
            for idx, line in enumerate(order.optional_spec_ids.sorted("sequence")):
                update_vals = {"sequence": idx + 1}
                if idx < len(OPTIONAL_SPEC_DEFAULTS):
                    update_vals["name"] = OPTIONAL_SPEC_DEFAULTS[idx][0]
                line.with_context(allow_protected_fields=True).write(update_vals)

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Hide the standard Optional Products tab in the sale order form."""
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type != "form":
            return res
        res["arch"] = self._hide_standard_optional_products_page(res.get("arch"))
        return res

    @api.model
    def _hide_standard_optional_products_page(self, arch):
        if not arch:
            return arch

        try:
            doc = etree.fromstring(arch)
        except Exception:
            return arch

        targets = doc.xpath("//page[@name='optional_products'] | //page[.//field[@name='optional_product_ids']]")
        if not targets:
            targets = doc.xpath("//page[contains(translate(@string, 'OPTIONAL', 'optional'), 'optional')]")

        for node in targets:
            node.set("invisible", "1")
            modifiers = json.loads(node.get("modifiers", "{}") or "{}")
            modifiers["invisible"] = True
            node.set("modifiers", json.dumps(modifiers))

        return etree.tostring(doc, encoding="unicode")

    def action_print_selected_quotation(self):
        self.ensure_one()
        if not self.quotation_type:
            raise UserError(_("Select a quotation type before printing."))

        if self.quotation_type == "laser":
            report = self.env.ref("laser_quotation_report.action_machine_quotation_report")
        elif self.quotation_type == "plasma":
            report = self.env.ref("laser_quotation_report.action_machine_quotation_powermax125_report")
        else:
            raise UserError(_("Unsupported quotation type."))

        return report.report_action(self)

    def _find_mail_template(self):
        self.ensure_one()
        if self.env.context.get('proforma') or self.state != 'sale':
            if self.quotation_type == "laser":
                return self.env.ref(
                    "laser_quotation_report.email_template_edi_sale_laser",
                    raise_if_not_found=False,
                )
            if self.quotation_type == "plasma":
                return self.env.ref(
                    "laser_quotation_report.email_template_edi_sale_plasma",
                    raise_if_not_found=False,
                )
        return super()._find_mail_template()


class SaleOrderOptionalSpec(models.Model):
    _name = "sale.order.optional.spec"
    _description = "Sale Order Optional Items"
    _order = "sequence, id"

    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        ondelete="cascade",
        required=True,
    )
    sequence = fields.Integer(string="Sr. No.", default=1)
    name = fields.Char(string="Description", required=True)
    value = fields.Char(string="Amount")

    def _default_name_from_sequence(self, seq):
        if 1 <= seq <= len(OPTIONAL_SPEC_DEFAULTS):
            return OPTIONAL_SPEC_DEFAULTS[seq - 1][0]
        return f"Item {seq}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                seq = vals.get("sequence") or 1
                vals["name"] = self._default_name_from_sequence(seq)
        return super().create(vals_list)

    def write(self, vals):
        vals = vals.copy()
        if not self.env.context.get("allow_protected_fields"):
            vals.pop("sequence", None)
            vals.pop("name", None)
        return super().write(vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    hsn_code = fields.Char(
        string="HSN Code",
        related="product_id.l10n_in_hsn_code",
        readonly=True,
    )
