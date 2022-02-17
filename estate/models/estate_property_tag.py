from dateutil.relativedelta import relativedelta
from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique"),
    ]

    _order = "name"

    name = fields.Char(required=True)
    color = fields.Char("Color Index")
