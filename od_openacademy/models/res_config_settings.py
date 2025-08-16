from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_number_of_seats = fields.Boolean('Number of Seats', config_parameter='od_openacademy.use_number_of_seats')
    session_number_of_seats = fields.Integer('Number of Seats', related='company_id.session_number_of_seats',
                                             readonly=False)
    module_od_openacademy_website = fields.Boolean("OpenAcademy Website")


class ResCompany(models.Model):
    _inherit = 'res.company'

    session_number_of_seats = fields.Integer('Number of Seats')
