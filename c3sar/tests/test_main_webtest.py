# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests
import unittest


class FunctionalTests(unittest.TestCase):
    """
    this test is a functional test to check functionality of the whole app

    it also serves to get coverage for 'main'
    """
    def setUp(self):
        # a few lines from
        # http://sontek.net/writing-tests-for-pyramid-and-sqlalchemy
        #import os
        #from sqlalchemy import engine_from_config
        #ROOT_PATH = os.path.join(os.path.dirname(__file__), '../..')
        #from paste.deploy.loadwsgi import appconfig
        #my123settings = appconfig(
        #    'config:' + os.path.join(ROOT_PATH, 'development.ini'))
        #engine = engine_from_config(my123settings, prefix='sqlalchemy.')

        my_settings = {'sqlalchemy.url': 'sqlite://'}  # mock, not even used!?
        from sqlalchemy import engine_from_config
        engine = engine_from_config(my_settings)

        #self.config.include('c3sar')
        from c3sar import main
        app = main({}, **my_settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        # maybe I need to check and remove globals here,
        # so the other tests are not compromised
        #del engine
        pass

    def test_z_root(self):
        """load the front page, check string exists"""
        res = self.testapp.get('/', status=200)
        self.failUnless('Basic Functionality' in res.body)
