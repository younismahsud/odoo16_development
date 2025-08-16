from odoo import models
import re


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _create_lead_livechat(self):
        live_chat_channel = self.env.user.company_id.website_id.channel_id
        channel_ids = self.env['mail.channel'].search([
            ('livechat_channel_id', '=', live_chat_channel.id), ('crm_lead_id', '=', False)])
        for channel in channel_ids:
            message_id = self.env['mail.message'].search([
                ('res_id', '=', channel.id), ('model', '=', 'mail.channel')], order='id asc', limit=1)
            html_message = message_id.body or ''
            channel_name = channel.display_name
            if html_message:
                pattern = r'<.*?>'
                message = re.sub(pattern, '', html_message)
                lead_id = self.create({
                    'name': channel_name,
                    'description': message,
                })
                lead_id.message_post(body=message)
                channel.write({'crm_lead_id': lead_id.id})
                if len(message) > 30:
                    admin_user = self.env.ref('base.user_admin')
                    task_id = self.env['project.task'].create({
                        'name': channel_name,
                        'description': message,
                        'user_ids': admin_user.ids
                    })
