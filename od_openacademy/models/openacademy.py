from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Course(models.Model):
    _name = 'od_openacademy.course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Title', required=True, translate=True)
    code = fields.Char('Code', copy=False, required=True, default='New', readonly=True)
    description = fields.Text(string='Description')
    course_date = fields.Date('Date', required=True, tracking=True)
    responsible_id = fields.Many2one('res.users', ondelete='set null', tracking=True)
    session_ids = fields.One2many('od_openacademy.session', 'course_id', string="Sessions")
    state = fields.Selection([
        ('draft', 'Draft'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancel', 'Cancel')
    ], string="Status", required=True, default='draft', tracking=True)
    company_info = fields.Char(company_dependent=True, string='Company Info')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    tag_ids = fields.Many2many('openacademy.course.tag', string='Tags')

    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.env['od_openacademy.course'].search_count([('name', '=like', f"Copy of {self.name}%")])
        if not copied_count:
            new_name = f"Copy of {self.name}"
        else:
            new_name = f"Copy of {self.name} ({copied_count})"
        default.update({'name': new_name})
        return super().copy(default=default)

    def button_in_progress(self):
        for course in self:
            course.write({'state': 'in_progress'})

    def button_completed(self):
        for course in self:
            course.write({'state': 'completed'})

    def button_cancel(self):
        for course in self:
            course.write({'state': 'cancel'})

    def button_draft(self):
        for course in self:
            course.write({'state': 'draft'})

    @api.model_create_multi
    def create(self, vals_list):
        sequence_code = 'openacademy.course'
        for vals in vals_list:
            course_date = vals.get('course_date')
            course_code = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=course_date)
            vals['code'] = course_code
        return super().create(vals_list)

    def get_total_seats(self):
        return sum(self.session_ids.mapped('seats'))
        # total_seats = 0
        # for session in self.session_ids:
        #     total_seats += session.seats
        # return total_seats

    _sql_constraints = [
        ('check_name_and_description', 'CHECK(name != description)', 'Title and Description must be different.'),
        ('name_unique', 'UNIQUE(name)', 'Course title must be unique.')
    ]


class OpenacademyTag(models.Model):
    _name = 'openacademy.course.tag'
    _description = 'Course Tag'

    name = fields.Char('Name', required=True, translate=True)


class Session(models.Model):
    _name = 'od_openacademy.session'
    _description = "OpenAcademy Sessions"
    _check_company_auto = True

    def _compute_current_date(self):
        return fields.Date.context_today(self)

    def get_default_number_of_seats(self):
        use_number_of_seats = self.env['ir.config_parameter'].get_param('od_openacademy.use_number_of_seats')
        if use_number_of_seats:
            company = self.env.company
            seats = company.session_number_of_seats
            return seats
        return 0

    name = fields.Char(required=True, translate=True)
    start_date = fields.Date(string="Start Date", default=_compute_current_date)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats", default=get_default_number_of_seats)
    instructor_id = fields.Many2one('res.partner', string='Instructor', ondelete='restrict', check_company=True)
    course_id = fields.Many2one('od_openacademy.course', string="Course", ondelete='cascade')
    attendee_ids = fields.Many2many('res.partner', 'session_res_partner', 'session_id', 'attendee_id', string='Attendees')
    taken_seats = fields.Float(string="Taken Seats", compute='_compute_taken_seats')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', related='course_id.company_id')

    @api.constrains('instructor_id', 'attendee_ids')
    def check_instructor_as_attendee(self):
        for record in self:
            if record.instructor_id.id in record.attendee_ids.ids:
                raise ValidationError(_("You can not add instructor as attendee!"))

    @api.onchange('seats', 'attendee_ids')
    def _onchange_seats_attendees(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Something bad happened",
                    'message': "You can not add negative value.",
                }
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Something bad happened",
                    'message': "You can not add more attendees then number of seats.",
                }
            }

    @api.depends('attendee_ids', 'seats')
    def _compute_taken_seats(self):
        for session in self:
            if session.seats == 0:
                session.taken_seats = 0
            else:
                session.taken_seats = (len(session.attendee_ids)/session.seats) * 100

    @api.model_create_multi
    def create(self, vals):
        sessions = super(Session, self).create(vals)
        for session in sessions:
            msg = f"A new session with the name {session.name} has been added."
            session.course_id.message_post(body=msg)
        return sessions

    def write(self, vals):
        self._log_session_tracking(vals)
        return super().write(vals)

    def _log_session_tracking(self, vals):
        template_id = 'od_openacademy.track_session_template'
        for session in self:
            data = {}
            if session.course_id.state == 'in_progress':
                if 'instructor_id' in vals:
                    data.update({'instructor_name': self.env['res.partner'].browse(vals.get('instructor_id')).name})
                if 'start_date' in vals:
                    data.update({'start_date': vals.get('start_date')})
            if data:
                session.course_id.message_post_with_view(template_id, values={'session': session, 'data': data})