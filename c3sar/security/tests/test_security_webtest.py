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
