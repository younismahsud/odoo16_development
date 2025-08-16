from collections import OrderedDict

from markupsafe import Markup

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

from odoo.osv.expression import OR


class OdooDiscussions(http.Controller):

    @http.route('/odoodiscussions/courses', auth='public', website=True)
    def display_data(self, **kwargs):
        return "<h1> This is Odoo Discussions </h1>"

    @http.route('/odoodiscussions/sessions', auth='public', website=True)
    def display_sessions(self, **kwargs):
        return "This is Odoo Discussions Sessions"

    def _get_sale_searchbar_sortings(self):
        return {
            'course_date': {'label': _('Course Date'), 'course': 'course_date desc'},
            'code': {'label': _('Code'), 'course': 'code'},
        }

    def _course_get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
            search_domain.append([('description', 'ilike', search)])
        return OR(search_domain)

    @http.route('/odoodiscussions/classes', auth='public', website=True, type='http')
    def odoodiscussions_classes(self, sortby=None, filterby=None, search=None, search_in='content', **kwargs):
        if sortby is None:
            sortby = 'course_date'

        searchbar_sortings = self._get_sale_searchbar_sortings()

        sort_course = searchbar_sortings[sortby]['course']

        states = ['draft', 'in_progress', 'completed', 'cancel']
        searchbar_filters = {
            'all': {'label': _('All States'), 'domain': [('state', 'in', states)]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'in_progress': {'label': _('In Progress'), 'domain': [('state', '=', 'in_progress')]},
        }

        if not filterby:
            filterby = 'all'

        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if search and search_in:
            domain += self._course_get_search_domain(search_in, search)

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'content': {'input': 'content', 'label': _('Search in Content'), 'order': 1},
        }

        courses = request.env['od_openacademy.course'].search(domain, order=sort_course)
        values = {
            "message": "Hello Odoo Discussions",
            "courses": courses,
            'page_name': 'course',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/odoodiscussions/classes',
        }
        return request.render('od_openacademy_website.portal_my_classes', values)

    @http.route("/odoodiscussions/<model('od_openacademy.course'):course>", auth='public', website=True, type='http')
    def display_name(self, course):
        template = "od_openacademy_website.odoodiscussions_course"
        return request.render(template, {'course': course, 'page_name': 'course'})
        # return f"Here this is the entered id = {course}"


class CustomerPortalDiscussions(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        values['course_count'] = request.env['od_openacademy.course'].search_count([])
        return values