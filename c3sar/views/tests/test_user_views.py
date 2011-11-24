# -*- coding: utf-8 -*-
import unittest
from pyramid import testing

import pprint
pp = pprint.PrettyPrinter(indent=4)

DEBUG = True

def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://testing.userviews.db')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

class UserViewIntegrationTests(unittest.TestCase):
    """
    We test the views in c3sar.views.user.py
    """
    def setUp(self):
        #self.session = _initTestingDB()
        import c3sar
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')
        from c3sar.models import DBSession, User
        DBSession.remove()

    def tearDown(self):
        #self.session.remove()
        testing.tearDown()

    def _getTargetClass(self):
        from c3sar.models import User
        return User

    def _makeUser(self, 
                  username=u'firstUsername', surname=u'firstSurname',
                  lastname=u'firstLastname',password=u'password',
                  email = u'first1@shri.de', 
                  email_confirmation_code = u'barfbarf',
                  email_is_confirmed=True,
                  phone=u'+49 6421 968300422',
                  fax=u'+49 6421 690 6996'
                  ):
        return self._getTargetClass()(
            username,password,surname,lastname,
            email,email_is_confirmed,email_confirmation_code,
            phone, fax)

    def test_user_register_view(self):
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = user_register(request)
        #print "--- in test_user_register_view()"
        #pp.pprint(result)
        
        # test: a form exists 
        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')
        

    def test_user_register_not_validating(self):
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        request.POST = {'username': "foo"}
        self.config = testing.setUp(request=request)
        result = user_register(request)
        #print "--- test_user_register_not_validating()"
        #pp.pprint(result)
        
        # test: form exists
        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')
        # TODO: test that form is not validating...
        # maybe rather a functional test?
      
    def test_user_confirm_email_view(self):
        """
        a test for the user_email_confirm view
        """
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        instance = self._makeUser()

        # mock values: /user/confirm/SSEFP0/c/c@shri.de
        request.matchdict['code'] = u'SSEFP0' # instance.email_confirm_code
        request.matchdict['user_name'] = u'c' # instance.username
        request.matchdict['user_email'] = u'c@shri.de' #instance.email

        result = user_confirm_email(request)
        #pp.pprint(result)
        #TODO
        


class BasicViewIntegrationTests(unittest.TestCase):

    def setUp(self):
        """
        This sets up the application registry with the registrations
        your application declares in its ``ìncludeme`` function
        """
        #self.session = _initTestingDB()
        #import c3sar
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')
        from c3sar.models import DBSession, User
        DBSession.remove()

    def tearDown(self):
        """clear out the application registry"""
        #self.session.remove()
        testing.tearDown()

    # def _getTargetClass(self):
    #     from c3sar.models import User
    #     return User

    # def _makeOne(self, name


    def test_home_view(self):
        from c3sar.views.basic import home_view
        from c3sar.models import DBSession
        dbsession = DBSession
        request = testing.DummyRequest()
        #self.config = testing.setUp(request=request)
        result = home_view(request)
        #print " "
        #print "dir(result): " + str(dir(result))
        #print "type(result): " + str(type(result))
        #print "type(result.items): " + str(type(result.items))
        #print "dir(result.items): " + str(dir(result.items))
        #print "result, prettyprinted: "
        #pp.pprint(result)
        # print "help(result.items): " + str(help(result.items))
        # print "result.viewkeys(): " + str(result.viewkeys())
        # print "help(result.viewkeys()): " + str(help(result.viewkeys()))
        #for item in result:
        #    print item
        
        #self.assertEqual(result.status, '200 OK', "not 200 OK")   # Todo
        
        #        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')
        #if DEBUG:
        #    print "--- in c3sar.tests.test_user_views.BasicViewIntegrationTests.test_home_view()"
        
        
