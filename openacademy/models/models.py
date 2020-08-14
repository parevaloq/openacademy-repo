# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

def get_uid(self, *a):
	return self.env.uid

class Course(models.Model):
    _name = 'openacademy.course'

    name = fields.Char(string="Title",required=True)
    description = fields.Text()
    responsible_id = fields.Many2one(
    	'res.users', string="Responsible",
    	index=True, ondelete='set null', 
    	default=lambda self, *a: self.env.uid)
        #default=get_uid)
    session_ids = fields.One2many('openacademy.session', 'course_id')


class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today) 
    datetime_test = fields.Datetime(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')) 
    datetime_test2 = fields.Datetime(default=fields.Datetime.now) 
    duration= fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)

    instructor_id = fields.Many2one('res.partner', string='Instructor', domain=['|',('instructor','=',True),('category_id.name','ilike','Teacher')])
    course_id = fields.Many2one('openacademy.course', ondelete='cascade',
    							string='Course', required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats
