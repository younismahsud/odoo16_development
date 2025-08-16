from odoo.addons.project.controllers.portal import ProjectCustomerPortal
from odoo.http import request
from odoo import _


class ODProjectCustomerPortal(ProjectCustomerPortal):

    def _get_my_tasks_searchbar_filters(self, project_domain=None, task_domain=None):
        searchbar_filters = super()._get_my_tasks_searchbar_filters(project_domain, task_domain)
        stage_ids = request.env['project.task.type'].search([('user_id', '=', False)])
        searchbar_filters.update({
            'all_stages': {'label': _('All Stages'), 'domain': [('stage_id', 'in', stage_ids.ids)]}
        })
        for stage in stage_ids:
            searchbar_filters.update({
                f"stage_{stage.id}": {'label': stage.name, 'domain': [('stage_id', '=', stage.id)]}
            })
        return searchbar_filters