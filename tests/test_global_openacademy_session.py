from psycopg2 import IntegrityError
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger
from openerp.exceptions import ValidationError

class GlobalTestOpenAcademySession(TransactionCase):
    '''
    This create global test to sessions
    '''

    #seudo-constructor method
    def setUp(self):
        super(GlobalTestOpenAcademySession, self).setUp()
        self.session = self.env['openacademy.session']
        self.parther_aux = self.env.ref('base.res_partner_address_3')
        self.parther_attendee = self.env.ref('base.res_partner_address_1')
        self.course_aux = self.env.ref('openacademy.course1')


    #generic methods
    def test_10_instructor_is_attendee(self):
        '''
        Check tat raise of 'A session's instructor can't be an attendee'
        '''

        with self.assertRaisesRegexp(ValidationError, "A session instructor cant'n be an attendee"):
            self.session.create({
                'name':'Session test 1',
                'seats': 1,
                'instructor_id': self.parther_aux.id,
                'attendee_ids':[(6, 0, [self.parther_aux.id])],
                'course_id': self.course_aux.id,
            })



    def test_20_wkf_done(self):
        '''
        Check that the workflow work fine
        '''

        self.session.create({
            'name':'Session test 1',
            'seats': 1,
            'instructor_id': self.parther_aux.id,
            'attendee_ids':[(6, 0, [self.parther_attendee.id])],
            'course_id': self.course_aux.id,
        })