# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

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

def _registerRoutes(config):
    config.add_route('register', '/register')
    config.add_route('confirm_email', '/user/confirm/{user_name}/{user_email}')
    config.add_route('user_list', '/user/list')
    config.add_route('user_view', '/user/view{user_id}')
    config.add_route('user_profile', '/user/profile/{user_id}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('user_login_first', '/sign_in_first')
    config.add_route('home', '/') # for logout_view redirect
    config.add_route('not_found', '/not_found') # for logout_view redirect
    #config.add_route('', '/')


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

    def _makeUser2(self,
                  username=u'secondUsername', surname=u'secondSurname',
                  lastname=u'secondLastname',password=u'password',
                  email = u'second2@shri.de',
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
        """
        test the register view -- without validating the form
        """
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        request.POST = {'username': "foo"}
        self.config = testing.setUp(request=request)
        result = user_register(request)

        # test: form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # test: form is not validated
        self.assertTrue(not result['form'].form.is_validated, 
                        'form validated unexpectedly.')
        # TODO: test that form is not validating...
        # maybe rather a functional test?

    def test_user_confirm_email_view(self):
        """
        a test for the user_email_confirm view -- non-validating
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
        self.assertEquals(
            result['result_msg'],
            "Something didn't work. Please check whether you tried the right URL.")
        #TODO... fix this.
        #how to supply the parameters and make validation work?

    def test_user_login_view(self):
        """
        testing the login view -- basic form
        """
        from c3sar.views.user import login_view
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = login_view(request)
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        
    def test_user_login_view_wrong_username(self):
        """
        testing the login view -- try to log in with a wrong username
        """
        from c3sar.views.user import login_view
        request = testing.DummyRequest(
            post={'submit':True,
                  'username':u'paul',
                  'password':u'pass'})
        self.config = testing.setUp(request=request)

        self.assertEquals(request.POST,{'submit': True,
                                        'password': 'pass',
                                        'username': 'paul'})
        result = login_view(request)

        # test: form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # test: form does not validate
        self.assertTrue(not result['form'].form.validate())
        # test: unknown username
        self.assertEquals(result['form'].form.errors,
                          {'username': 'That username does not exist'},
                          "expected error message not found")

    def test_user_login_view_valid_user_invalidChar_pw(self):
        """
        login view - try login with valid user but invalid characters in password
        """
        from c3sar.views.user import login_view
        my_user = self._makeUser()
        self.dbsession.add(my_user)
        request = testing.DummyRequest(
            post={'submit': True,
                  'username': my_user.username,
                  'password': 'schmööp schmööp'})
        self.config = testing.setUp(request=request)
        result = login_view(request)

        #pp.pprint( result)
        #import pdb
        #pdb.set_trace()

        # test: form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # test: form does not validate
        self.assertTrue(not result['form'].form.validate(),
                        "the form should not validate,"
                        "because of invalid chars in password")
        # test: unknown username
        self.assertEquals(
            result['form'].form.errors,
            {'password': u'Enter only letters, numbers, or _ (underscore)'},
            "expected error message was not found")

    def test_user_login_view_valid_user_wrong_pw(self):
        """
        login view - try login with a valid username but wrong password
        """
        from c3sar.views.user import login_view
        my_user = self._makeUser()
        self.dbsession.add(my_user)
        request = testing.DummyRequest(
            post={'submit': True,
                  'username': my_user.username,
                  'password': 'N0T_THE_RIGHT_PW_but_a_v4l1d_0nE'})
        self.config = testing.setUp(request=request)
        result = login_view(request)

        #pp.pprint( result)
        #import pdb
        #pdb.set_trace()

        # test: form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # test: form does not validate
        self.assertTrue(result['form'].form.validate(),
                        "the form should validate, even with a wrong password")
        # test: unknown username
        self.assertEquals(
            result['form'].form.errors,
            {},
            "expected NO error message")

    def test_user_login_view_valid_user_and_pw(self):
        """
        test login view -- try to log in with a valid username and pw
        """
        from c3sar.views.user import login_view
        _registerRoutes(self.config)
        my_user = self._makeUser()
        self.dbsession.add(my_user)
        request = testing.DummyRequest(
            post={'submit':True,
                  'username':my_user.username,
                  'password': 'password'}) # the right password
        self.config = testing.setUp(request=request)

        #import pdb
        #pdb.set_trace()

        #result = login_view(request)
        # XXX TODO: this one borks! but why?
        #
        #(Pdb) self.config.package.url.route_url('home', request)
        #*** ComponentLookupError: (<InterfaceClass pyramid.interfaces.IRoutesMapper>, u'')
        #(Pdb) self.config.package.url.route_url('login', request)
        #*** ComponentLookupError: (<InterfaceClass pyramid.interfaces.IRoutesMapper>, u'')

        #print "the result: "
        #pp.pprint(result)

        # test: view returns a redirect
        #self.assertTrue(isinstance(result, HTTPFound))

        # # test: form exists
        # self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # # test: form does not validate
        # self.assertTrue(not result['form'].form.validate())


    def test_logout_view(self):
        """
        test the logout view
        """
        from c3sar.views.user import logout_view
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = logout_view(request)

        # test: view returns a redirect
        self.assertTrue(isinstance(result, HTTPFound))

        #print "result: " + str(pp.pprint(result))
        #print "result.body: " + str(pp.pprint(result.body))
        #print "result.headers: " + str(pp.pprint(result.headers))
        #print "result.location: " + str(pp.pprint(result.location))

    def test_user_list(self):
        """
        test the user_list view

        with empty database: no users listed
        """
        from c3sar.views.user import user_list
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = user_list(request)

        #print "result: "
        #pp.pprint(result)

        # test: view returns a dict
        self.assertEquals(result, {'users': []})

        #print "result['users']: "
        #pp.pprint(result['users'])
        # test: view returns an empty list of users
        self.assertTrue(result['users'] ==  [])

    def test_user_list_one(self):
        """
        test the user_list view

        with one user instance in database
        """
        from c3sar.views.user import user_list
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        instance = self._makeUser()
        self.dbsession.add(instance)
        result = user_list(request)

        # test: view returns a dict conaining a list of users
        # with ONE user, so not empty
        self.assertNotEquals(result, {'users': []})

        # test: view returns a non empty list of users
        self.assertTrue(not result['users'] ==  [])

        #print "result: "
        #pp.pprint(result)
        #print "result['users'][0]: "
        #pp.pprint(result['users'][0].username)
        self.assertEquals(result['users'][0].username, instance.username)

    def test_user_list_two(self):
        """
        test the user_list view

        with two users in database
        """
        from c3sar.views.user import user_list
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        instance = self._makeUser()
        self.dbsession.add(instance)
        instance2 = self._makeUser2()
        self.dbsession.add(instance2)
        result = user_list(request)

        # test: view returns a dict conaining a list of users
        # with TWO users, so not empty
        self.assertNotEquals(result, {'users': []})

        # test: view returns a non empty list of users
        self.assertTrue(not result['users'] ==  [])

        #print "result: "
        #pp.pprint(result)
        #print "result['users'][0]: "
        #pp.pprint(result['users'][0].username)
        #pp.pprint(result['users'][1].username)
        self.assertEquals(result['users'][0].username, instance.username)
        self.assertEquals(result['users'][1].username, instance2.username)

    def test_user_view_returns_redirect(self):
        """
        test the user_view view
        
        if no user with user_id exists
        expect a redirect to not_found view
        """
        from c3sar.views.user import user_view
        request = testing.DummyRequest()
        request.matchdict['user_id'] = '1'
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = user_view(request)

        #print "result: "
        #pp.pprint(result)

        # test: view returns a redirect
        self.assertTrue(isinstance(result, HTTPFound))

    def test_user_view(self):
        """
        test the user_view view

        if a user with user_id from URL exists,
        
        """
        from c3sar.views.user import user_view
        request = testing.DummyRequest()
        request.matchdict['user_id'] = '1'
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        instance = self._makeUser()
        self.dbsession.add(instance)

        result = user_view(request)

        #print "result: "
        #pp.pprint(result)

        #print "result['user'].username: "
        #pp.pprint(result['user'].username)

        # test: view returns a dict containing a user
        self.assertEquals(result['user'].username, instance.username)

        #print "result['users']: "
        #pp.pprint(result['users'])
        # test: view returns an empty list of users
        #self.assertTrue(result['users'] ==  [])

    def test_user_profile(self):
        """
        test the user_profile view

        if a user with user_id from URL exists,
        
        """
        from c3sar.views.user import user_profile
        request = testing.DummyRequest()
        request.matchdict['user_id'] = '1'
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        instance = self._makeUser()
        self.dbsession.add(instance)

        result = user_profile(request)

        #print "result: "
        #pp.pprint(result)
        #print "result['user'].username: "
        #pp.pprint(result['user'].username)

        # test: view returns a dict containing a user
        self.assertEquals(result['user'].username, instance.username)

