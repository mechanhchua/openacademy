# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models

# lop C
class Course(models.Model):
    # ten model la openacademy, mieu ta la Couse
    _name = 'openacademy.course'
    _description = 'Course'
    # ten couse la chuoi, mieu ta dang text
    name = fields.Char(name='Title', required=True)
    description = fields.Text()
    # thanh xo xuong 3 gia tri
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible")
    # mot cot mang gia tri cac course_id, ten cot la Sessions
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")
    # xo xuong 3 muc do cua cap hoc ten cot la Difficulty Level kieu chuoi
    level = fields.Selection([(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], string="Difficulty Level")
    session_count = fields.Integer(compute="_compute_session_count")
    # ham dem so luong couse theo self
    @api.depends('session_ids')
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)


class Session(models.Model):
    # ten model la openacademy, mieu ta la session
    _name = 'openacademy.session'
    _description = 'Session'
    #ten file dang chuoi
    name = fields.Char(required=True)
    #mieu ta Html
    description = fields.Html()
    # trang thai dang True hoac False
    active = fields.Boolean(default=True)
    #trang thai khoa hoc la Draft, confirmed, done va neu khong tu chon se dat mac dinh la draft
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed"), ('done', "Done")], default='draft')
    level = fields.Selection(related='course_id.level', readonly=True)
    responsible_id = fields.Many2one(related='course_id.responsible_id', readonly=True, store=True)
    #ngay bat dau khoa hoc, ngay ket thuc khoa hoc, qua trinh hoc
    start_date = fields.Date(default=fields.Date.context_today)
    end_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=1)

    # instructor dang many2one, mot cot, ten cot la instructor
    instructor_id = fields.Many2one('res.partner', string="Instructor")
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    attendees_count = fields.Integer(compute='_get_attendees_count', store=True)
    seats = fields.Integer()
    taken_seats = fields.Float(compute='_compute_taken_seats', store=True)

    @api.depends('seats', 'attendee_ids')
    # ham dem so luong vi tri lop hoc da duoc dang ky
    def _compute_taken_seats(self):
        for session in self:
            if not session.seats:
                session.taken_seats = 0.0
            else:
                session.taken_seats = 100.0 * len(session.attendee_ids) / session.seats

    # dem so luong khoa hoc
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for session in self:
            session.attendees_count = len(session.attendee_ids)

   # tinh so ngay tu luc bat dau khoa hoc den luc ket thuc khoa hoc, neu ngay ket thuc < ngay bat dau thi warning
    @api.onchange('start_date', 'end_date')
    def _compute_duration(self):
        if not (self.start_date and self.end_date):
            return
        if self.end_date < self.start_date:
            return {'warning': {
                'title':   "Incorrect date value",
                'message': "End date is earlier then start date",
            }}
        delta = fields.Date.from_string(self.end_date) - fields.Date.from_string(self.start_date)
        self.duration = delta.days + 1
