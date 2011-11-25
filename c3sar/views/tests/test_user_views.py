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
    engine = create_engine('sqlite:///testing.userviews.db')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

class UserViewIntegrationTests(unittest.TestCase):
    """
    We test the views in c3sar.views.user.py
    """
    def setUp(self):
        self.dbsession = _initTestingDB()
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')
        self.dbsession.remove()

    def tearDown(self):
        import transaction
        transaction.abort()
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
        # test: a form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')


    def test_user_register_not_validating(self):
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        request.POST = {'username': "foo"}
        self.config = testing.setUp(request=request)
        result = user_register(request)
        #print "--- test_user_register_not_validating()"
        pp.pprint(result.items())

        # test: form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # test: form is not validated
        self.assertTrue(not result['form'].form.is_validated, 
                        'form validated unexpectedly.')
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
        request.matchdict['code'] = instance.email_confirm_code
        request.matchdict['user_name'] =  instance.username
        request.matchdict['user_email'] = instance.email

        result = user_confirm_email(request)
        #pp.pprint(result)
        #TODO
        #import pdb 
        #pdb.set_trace()
        # result['result_msg']
        self.assertEquals(
            result['result_msg'],
            "Something didn't work. Please check whether you tried the right URL.")
        #TODO... fix this.
        #how to supply the parameters and make validation work?

    def test_user_login_view(self):
        """
        testing the login view
        """
        from c3sar.views.user import login_view
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = login_view(request)
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        
