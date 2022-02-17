from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from odoo.exceptions import UserError

from odoo.tools import float_compare


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _sql_constraints = [
        ("check_price", "check(price>=0)", "An offer price must be strictly positive")
    ]
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        string = 'Status',
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
        default=False,
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required="True")
    property_id = fields.Many2one("estate.property", string="Property",required="True")
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    )
    validity = fields.Integer("validity", default=7)

    date_deadline = fields.Date("Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for data in self:
            date = data.create_date.date() if data.create_date else fields.Date.today()
            data.date_deadline = date + relativedelta(days=data.validity)

    def _inverse_date_deadline(self):
        for data in self:
            date = data.create_date.date() if data.create_date else fields.Date.today()
            data.validity = (data.date_deadline - date).days

    def action_accept(self):
        if "accepted" in self.mapped("property_id.offer_ids.status"):
            raise UserError("An offer as already been accepted.")
        self.write({'status': 'accepted'})
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price" : self.price,
                "buyer_id": self.partner_id.id,
            }
        )

    def action_refuse(self):
        return self.write({'status': 'refused'})

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)
