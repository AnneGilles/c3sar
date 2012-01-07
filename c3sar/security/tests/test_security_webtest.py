# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests

import unittest
import pprint
pp = pprint.PrettyPrinter(indent=4)


class FunctionalTests(unittest.TestCase):
    """
    test the whole application the WebTest way
    """
    def setUp(self):
        mock_settings = {'sqlalchemy.url': 'sqlite://'}  # mock
        from sqlalchemy import engine_from_config
        engine = engine_from_config(mock_settings)

        from c3sar import main
        app = main({}, **mock_settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        from c3sar.models import DBSession
        DBSession.remove()

    def test_a_user_factory(self):
        """edit a user

        side effect: test coverage for c3sar.security.UserFactory"""
        res1 = self.testapp.get('/login')

        # load form, fill form, submit form
        form = res1.form
        form['username'] = 'firstUsername'
        form['password'] = 'password'
        res2 = form.submit('submit')

        # so now firstUsername is logged in
        # let's check she may edit her details
        res3 = self.testapp.get('/user/edit/2')
        #print res3.body
        #
        # but not other users stuff
        res4 = self.testapp.get('/user/edit/1', status=403)
        res5 = self.testapp.get('/user/edit/3', status=403)
        #
        res6 = self.testapp.get('/')
        # make sure the username can be read in the page contents
        # to verify being still logged in
        self.failUnless('firstUsername' in res6.body)

    def test_b_track_factory(self):
        """edit a track

        side effect: test coverage for c3sar.security.TrackFactory"""

        # without login, track creation is forbidden
        res0 = self.testapp.get('/track/add', status=403)

        # so go to login page
        res1 = self.testapp.get('/login')
        # load form, fill form, submit form
        form = res1.form
        form['username'] = 'firstUsername'
        form['password'] = 'password'
        res2 = form.submit('submit')

        # go to main page, check username display
        res3 = self.testapp.get('/')
        self.failUnless('firstUsername' in res3.body)

        # so now firstUsername is logged in
        # let's check she may add & edit tracks
        # and thus test TrackFactory
        res5 = self.testapp.get('/track/add')
        #print res5.body
        #print "=== the /track/add form: ==="
        track_add_form = res5.form
        #pp.pprint(track_add_form.action)  # u'http://localhost/track/add'
        #pp.pprint(track_add_form.method)  # u'post'
        #pp.pprint(track_add_form.fields.values())
        #
        # fill in the form
        track_add_form['track_name'] = 'a test track'
        track_add_form['track_album'] = 'a test album'
        res5_added = track_add_form.submit('form.submitted')

        # print res5_added.body
        self.failUnless('302 Found' in res5_added.body)
        self.failUnless('The resource was found at' in res5_added.body)
        self.failUnless('you should be redirected automatically.'
                        in res5_added.body)
        #print "=== res5_added.headers "
        #print res5_added.headers
        #print "=== end of res5_added.headers "
        #
        # check that we get a redirect after submitting the form
        self.failUnless('Location' in res5_added.headers)
        self.failUnless("('Location', 'http://localhost/track/view/3')"
                        in str(res5_added.headers))

        # now try to edit tracks
        res5a = self.testapp.get('/track/edit/1', status=403)  # forbidden
        res5b = self.testapp.get('/track/edit/2', status=403)  # forbidden
        res5c = self.testapp.get('/track/edit/3')              # allowed
        # chck that the given name is present
        self.failUnless('a test track' in res5c.body)
        #
        res6 = self.testapp.get('/')
        # make sure the username can be read in the page contents
        self.failUnless('firstUsername' in res6.body)

    def test_z_login(self):
        """sign in via login form

        side effect: test coverage for c3sar.security.request"""
        res1 = self.testapp.get('/login')

        #pp.pprint(form.action)
        #pp.pprint(form.method)
        #pp.pprint(form.fields.values())

        # load form, fill form, submit form
        form = res1.form
        form['username'] = 'firstUsername'
        form['password'] = 'password'
        res2 = form.submit('submit')
        #print "res2.body ----------------------"
        #print res2  # now we are logged in, right?

        # after this, go to root again. see if this covers
        # c3sar.security.request         10      1    90%   20
        #print "------- request.user: " + str(request.user)
        # mmmh request is not defined :-/
        res3 = self.testapp.get('/user/view/1')
        #print "res3.body ----------------------"
        #print res3.body
        # import pdb; pdb.set_trace()
        self.failUnless('information about' in res3.body,
                        "the expected string was not found")
