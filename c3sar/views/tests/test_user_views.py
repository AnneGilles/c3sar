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
    #DBSession.configure(bind=engine)
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
    config.add_route('home', '/')  # for logout_view redirect
    config.add_route('not_found', '/not_found')  # for user_view redirect
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
                  lastname=u'firstLastname', password=u'password',
                  email=u'first1@shri.de',
                  email_confirmation_code=u'barfbarf',
                  email_is_confirmed=True,
                  phone=u'+49 6421 968300422',
                  fax=u'+49 6421 690 6996'
                  ):
        return self._getTargetClass()(
            username, password, surname, lastname,
            email, email_is_confirmed, email_confirmation_code,
            phone, fax)

    def _makeUser2(self,
                  username=u'secondUsername', surname=u'secondSurname',
                  lastname=u'secondLastname', password=u'password',
                  email=u'second2@shri.de',
                  email_confirmation_code=u'barfbarf',
                  email_is_confirmed=False,
                  phone=u'+49 6421 968300422',
                  fax=u'+49 6421 690 6996'
                  ):
        return self._getTargetClass()(
            username, password, surname, lastname,
            email, email_is_confirmed, email_confirmation_code,
            phone, fax)

    def test_user_register_view(self):
        """
        register view -- form test
        """
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = user_register(request)
        # test: a form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')

    def test_user_register_not_validating(self):
        """
        register view -- without validating the form
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

    def test_user_register_submit(self):
        """
        register view -- submit but don't validate the form
        """
        from c3sar.views.user import user_register
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'username': u'foo',
                  'password': u'passfoo'})
        self.config = testing.setUp(request=request)
        result = user_register(request)

        #import pdb
        #pdb.set_trace()

        # test: form exists
        self.assertTrue('form' in result.items()[0], 'form was not seen.')
        # test: form does not validate
        self.assertTrue(not result['form'].form.validate(),
                        'form validated unexpectedly.')
        self.assertEquals(
            result['form'].form.errors,
            {
                'confirm_password': u'Missing value',
                'city': u'Missing value',
                'surname': u'Missing value',
                'lastname': u'Missing value',
                'number': u'Missing value',
                'phone': u'Missing value',
                'street': u'Missing value',
                'postcode': u'Missing value',
                'country': u'Missing value',
                'email': u'Missing value'
                },
            "not the expected validation error messages")

    def test_user_register_submit_validate(self):
        """
        register view -- and validate the form
        """
        from c3sar.views.user import user_register
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'username': u'foo',
                  'password': u'passfoo',
                  'confirm_password': u'passfoo',
                  'city': u'foocity',
                  'surname': u'surfooname',
                  'lastname': u'lastfooname',
                  'number': u'foonumber',
                  'phone': u'foophone',
                  'street': u'foostreet',
                  'postcode': u'foocode',
                  'country': u'fooland',
                  'email': u'foo@example.com',
                  'fax': '',
                  })
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = user_register(request)

        # test: view returns a redirect upon registration success
        self.assertTrue(isinstance(result, HTTPFound))

    def test_user_confirm_email_view_invalid_user(self):
        """
        email confirmation -- non-validating: invalid user
        """
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        # mock values: /user/confirm/SOME_CODE/foo/c@example.com
        request.matchdict['code'] = u"SOME_CODE"
        request.matchdict['user_name'] = u"foo"
        request.matchdict['user_email'] = u"foo@example.com"

        result = user_confirm_email(request)
        self.assertEquals(
            result['result_msg'],
            "Something didn't work. " +
            "Please check whether you tried the right URL.")

    def test_user_confirm_email_view_invalid_email(self):
        """
        email confirmation -- non-validating: valid user, invalid email

        e.g. a valid user with a valid code tries to confirm an invalid email
        """
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        instance = self._makeUser2()  # valid user
        self.dbsession.add(instance)

        # mock values: /user/confirm/SOME_CODE/foo/c@example.com
        request.matchdict['code'] = instance.email_confirm_code
        request.matchdict['user_name'] = instance.username
        request.matchdict['user_email'] = u"foo@example.com"

        result = user_confirm_email(request)
        self.assertEquals(
            result['result_msg'],
            "Verification has failed. Bummer!")

    def test_user_confirm_email_view_already_confrmd(self):
        """
        email confirmation view -- already confirmed
        """
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        instance = self._makeUser()
        self.dbsession.add(instance)

        request.matchdict['code'] = instance.email_confirm_code
        request.matchdict['user_name'] = instance.username
        request.matchdict['user_email'] = instance.email

        result = user_confirm_email(request)
        self.assertEquals(
            result['result_msg'],
            "Your email address was confirmed already.")

    def test_user_confirm_email_view(self):
        """
        email confirmation view -- working
        """
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        instance = self._makeUser2()
        self.dbsession.add(instance)

        request.matchdict['code'] = instance.email_confirm_code
        request.matchdict['user_name'] = instance.username
        request.matchdict['user_email'] = instance.email

        result = user_confirm_email(request)
        self.assertEquals(
            result['result_msg'],
            "Thanks! Your email address has been confirmed.")

    def test_user_login_view(self):
        """
        login view -- basic form
        """
        from c3sar.views.user import login_view
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = login_view(request)
        #self.assertTrue('form' in result['form'].form., 'form was not seen.')
        self.assertTrue(not result['form'].form.is_validated,
                        'form validated unexpectedly.')
    # def test_user_login_view_already_loggedin(self):
    #     """
    #     login view -- if already logged in
    #     """
    #     from c3sar.views.user import login_view
    #     #import pdb
    #     #pdb.set_trace()

    #     self.config.testing_securitypolicy(userid=u'username',
    #                                        permissive=True)
    #     request = testing.DummyRequest()
    #     self.config = testing.setUp(request=request)
    #     result = login_view(request)

    #     pp.pprint(result)

    #     #self.assertRaises(HTTPFound, login_view, request)
    #     #self.assertTrue(isinstance(result, HTTPFound))
    #     # TODO: fixme!
    #     # I think I hit the wall where
    #     # an integration test is needed to open a door and step through

    def test_user_login_view_wrong_username(self):
        """
        login view -- try to log in with a wrong username
        """
        from c3sar.views.user import login_view
        request = testing.DummyRequest(
            post={'submit': True,
                  'username': u'paul',
                  'password': u'pass'})
        self.config = testing.setUp(request=request)

        self.assertEquals(request.POST, {'submit': True,
                                        'password': 'pass',
                                        'username': 'paul'})
        result = login_view(request)

        # test: form does not validate
        self.assertTrue(not result['form'].form.validate())
        # test: unknown username
        self.assertEquals(result['form'].form.errors,
                          {'username': 'That username does not exist'},
                          "expected error message not found")

    def test_user_login_view_valid_user_invalidChar_pw(self):
        """
        login view - try login with valid user but invalid characters in passw
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
        login view -- try to log in with a valid username and pw
        """
        from c3sar.views.user import login_view
        my_user = self._makeUser()
        self.dbsession.add(my_user)
        request = testing.DummyRequest(
            post={'submit': True,
                  'username': my_user.username,
                  'password': 'password'})  # the right password
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)

        result = login_view(request)

        #pp.pprint(result) # <HTTPFound at ... 302 Found>

        # test: view returns a redirect
        self.assertTrue(isinstance(result, HTTPFound))

    def test_logout_view(self):
        """
        logout view
        """
        from c3sar.views.user import logout_view
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = logout_view(request)

        # test: view returns a redirect
        self.assertTrue(isinstance(result, HTTPFound))

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
        self.assertTrue(result['users'] == [])

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
        self.assertTrue(not result['users'] == [])

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
        self.assertTrue(not result['users'] == [])

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
        #self.assertTrue(result['users'] == [])

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

    def test_user_edit_view(self):
        """
        user edit view -- test return values
        """
        from c3sar.views.user import user_edit
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        instance = self._makeUser()
        self.dbsession.add(instance)
        self.dbsession.flush()
        request.matchdict['user_id'] = instance.id
        result = user_edit(request)
        # test values
        self.assertEquals(result['the_user_id'], instance.id, "wrong id")
        self.assertEquals(
            result['the_username'], instance.username, "wrong username")
        self.assertTrue(result['form'], "no form")
        # test: no errors
        self.assertEquals(
             result['form'].form.errors, {},
             "unexpected error message was found")

    def test_user_edit_view_no_userid_in_matchdict(self):
        """
        user edit view -- matchdict test & redirect

        if matchdict is invalid, expect redirect
        """
        from c3sar.views.user import user_edit
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        instance = self._makeUser()
        self.dbsession.add(instance)
        self.dbsession.flush()
        request.matchdict['user_id'] = 'foo'
        result = user_edit(request)
        # test: a redirect is triggered
        self.assertTrue(isinstance(result, HTTPFound), 'no redirect seen')

    def test_user_edit_non_validating(self):
        """
        user edit view -- without validating the form
        """
        from c3sar.views.user import user_edit
        request = testing.DummyRequest()
        request.POST = {'username': "foo"}
        self.config = testing.setUp(request=request)
        instance = self._makeUser()
        self.dbsession.add(instance)
        self.dbsession.flush()
        request.matchdict['user_id'] = instance.id
        result = user_edit(request)
        #print "user edit view -- without validating"
        #pp.pprint(result)
        # test: no errors
        self.assertEquals(
             result['form'].form.errors, {},
             "unexpected error message was found")

    def test_user_edit_submitted_non_validating(self):
        """
        user edit view -- without validating the form
        """
        from c3sar.views.user import user_edit
        request = testing.DummyRequest(
            post={
                'form.submitted': True,
                'username': u' ',  # <-- can't be edited anyways
                'password': u'passfoo',
                'confirm_password': u'passfoo',
                'city': u'foocity',
                'surname': u'',
                'lastname': u'lastfooname',
                'number': u'foonumber',
                'phone': u'foophone',
                'street': u'foostreet',
                'postcode': u'foocode',
                'country': u'fooland',
                'email': u'foo@example.com',
                'fax': '',
                })
        self.config = testing.setUp(request=request)
        instance = self._makeUser()
        self.dbsession.add(instance)
        self.dbsession.flush()
        request.matchdict['user_id'] = instance.id
        result = user_edit(request)
        #print "submitted non validating: "
        #pp.pprint(result)
        # self.assertEquals(result['user'].username, instance.username)
        #print  result['form'].form.errors

        # self.assertTrue(result['form'].form.is_validated,
        #                "form not validated?")
        #import pdb
        #pdb.set_trace()

        # test: empty surname --> validation error
        self.assertEquals(
             result['form'].form.errors, {'surname': u'Please enter a value'},
             "unexpected error message was found")

    def test_user_edit_submitted_validating(self):
        """
        user edit view -- without validating the form
        """
        from c3sar.views.user import user_edit
        request = testing.DummyRequest(
            post={
                'form.submitted': True,
                'username': u'bar',
                'password': u'passfoo',
                'confirm_password': u'passfoo',
                'city': u'foocity',
                'surname': u'surfooname',
                'lastname': u'lastfooname',
                'number': u'foonumber',
                'phone': u'foophone',
                'street': u'foostreet',
                'postcode': u'foocode',
                'country': u'fooland',
                'email': u'foo@example.com',
                'fax': '',
                })
        self.config = testing.setUp(request=request)
        instance = self._makeUser()
        self.dbsession.add(instance)
        self.dbsession.flush()
        request.matchdict['user_id'] = instance.id
        result = user_edit(request)
        #print "submitted non validating: "
        #pp.pprint(result)
        # self.assertEquals(result['user'].username, instance.username)
        #print  result['form'].form.errors

        # self.assertTrue(result['form'].form.is_validated,
        #                "form not validated?")
        #import pdb
        #pdb.set_trace()

        # test: unknown username
        self.assertEquals(
             result['form'].form.errors, {},
             "unexpected error message was found")

    def test_user_edit_submitted_invalid_email(self):
        """
        user edit view -- without validating the form
        """
        from c3sar.views.user import user_edit
        request = testing.DummyRequest(
            post={
                'form.submitted': True,
                'username': u'bar',
                'password': u'passfoo',
                'confirm_password': u'passfoo',
                'city': u'foocity',
                'surname': u'surfooname',
                'lastname': u'lastfooname',
                'number': u'foonumber',
                'phone': u'foophone',
                'street': u'foostreet',
                'postcode': u'foocode',
                'country': u'fooland',
                'email': u'example.com',  # <---------- invalid
                'fax': '',
                })
        self.config = testing.setUp(request=request)
        instance = self._makeUser()
        self.dbsession.add(instance)
        self.dbsession.flush()
        request.matchdict['user_id'] = instance.id
        result = user_edit(request)
        #print "submitted invalid email: "
        #pp.pprint(result)
        # self.assertEquals(result['user'].username, instance.username)
        #print  result['form'].form.errors

        self.assertTrue(not result['form'].form.validate(),
                        "the form should not have validated!")
        #import pdb
        #pdb.set_trace()

        # test: unknown username
        self.assertEquals(
             result['form'].form.errors,
             {'email': u'An email address must contain a single @'},
             "unexpected error message was found")
