# _*_ encoding: utf-8 -*-

from psycopg2 import IntegrityError
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger

class GlobalTestOpenAcademyCourse(TransactionCase):
    '''
    Global test to openacademy course model
    Test coreate course and trigger constraits
    '''

    #method seudo-constructor of test setUp
    def setUp(self):
        #Define global variables to test methods
        super(GlobalTestOpenAcademyCourse, self).setUp()
        self.course = self.env['openacademy.course']



    #method class that don't is test
    def create_course(self, name, description, course_responsible_id):
        #create a course with parameters recived
        course_id = self.course.create({
            'name': name,
            'description': description,
            'responsible_id': course_responsible_id,
            })
        return course_id


    #method of test startswith 'def test_*(self):'

    #mute the error odoo.sql_db to avoid it in log
    @mute_logger('odoo.sql_db')
    def test_01_same_name_description(self):
        '''
        Test create a course with same name and description.
        To test contraint of name differente to description.
        '''
        #Error reaised expected with message expected
        with self.assertRaisesRegexp(IntegrityError, 'new row for relation "openacademy_course" violates check constraint "openacademy_course_name_description_check'):
            # create a course with same name and description to raise error
            self.create_course('test', 'test', None)


    @mute_logger('odoo.sql_db')
    def test_02_tow_courses_same_name(self):
        '''
        Test to create two courses with same name
        To raise constraint of unique name
        '''
        #with self.assertRaisesRegexp(IntegrityError, 'duplicate key value violates unique constraint "openacademy_course_name_unique"'):
        new_id = self.create_course('test1', 'test_description', None)
        print("new_id", new_id)

        with self.assertRaisesRegexp(IntegrityError, 'duplicate key value violates unique constraint "openacademy_course_name_unique"'):
            new_id2 = self.create_course('test1', 'test_description', None)
            print("new_id2", new_id2)


    def test_03_duplicate_course(self):
        '''
        Test to duplicate a course and check that work fine!
        '''
        course = self.env.ref('openacademy.course0')
        course_id = course.copy()
        print('course_id', course_id)