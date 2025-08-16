from odoo import models, fields


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
