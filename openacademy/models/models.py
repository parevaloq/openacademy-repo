# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions
import time

class Course(models.Model):
    _name = 'openacademy.course'
    _description="openacademy of test"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True, default=lambda self, *a: self.env.uid)
    session_ids = fields.One2many('openacademy.session', 'course_id')

    _sql_constraints =[
        ('name_description_check','CHECK(name != description)',"The title of the course should not be the description",),
        ('name_unique','UNIQUE(name)',"The course title must be unique",),
    ]


    def copy(self, default=None):
        if default is None:
            default= {}
        copied_count = self.search_count([('name', 'ilike', 'Copy of %s%%' % (self.name))])

        if not copied_count:
            new_name = "Copy of %s" % (self.name)
        else:
            new_name = "Copy of %s (%s)" % (self.name, copied_count)

        default['name'] = new_name

        #try:
        return super(Course, self).copy(default)
        #except IntegrityError:




class Session(models.Model):
    _name = 'openacademy.session'
    _description = "openacademy session of test"

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    datetime_test = fields.Datetime(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')) 
    datetime_test2 = fields.Datetime(default=fields.Datetime.now) 
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")

    instructor_id = fields.Many2one('res.partner', string="Instructor", domain=['|', ('instructor','=',True), ('category_id.name','ilike','Teacher')])
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(compute='_taken_seats', store=True)
    active = fields.Boolean(default=True)
    end_date = fields.Date(string="End Date", store=True, compute='_get_end_date', inverse='_set_end_date')
    hours = fields.Float(string="Duration in hours", compute='_get_hours', inverse='_set_hours')
    attendees_count = fields.Integer(string="Attendees count", compute='_get_attendees_count', store=True)
    color = fields.Integer()

    @api.depends('seats','attendee_ids')
    def _taken_seats(self):
        for record in self:
            if not record.seats:
                record.taken_seats = 0.0
            else:
                record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats


    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            self.active = False
            return {
                'warning':{
                    'title':"Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                }
            }

        if self.seats < len(self.attendee_ids):
            self.active = False
            return {
                'warning':{
                    'title':"Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                }
             }
        self.active = True

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendee(self):
        for record in self.filtered('instructor_id'):
            if record.instructor_id in record.attendee_ids:
                raise exceptions.ValidationError("A session instructor cant'n be an attendee")

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1

    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _set_hours(self):
        for r in self:
            r.duration = r.hours / 24
            
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)