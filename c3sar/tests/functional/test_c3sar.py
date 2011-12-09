# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests

import unittest
import pprint
pp = pprint.PrettyPrinter(indent=4)


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        from c3sar import main
        my_settings = {'sqlalchemy.url': 'sqlite://'}  # mock
        from sqlalchemy import engine_from_config
        engine = engine_from_config(my_settings)
        app = main({}, **my_settings)
        # if I try app = main({}) it tells me 'url' wasnt there, so I mock ^^
        from webtest import TestApp
        self.testapp = TestApp(app)
        # right here I would like to find DBSession and .remove() it !!!!!!!!!

    def tearDown(self):
        from c3sar.models import DBSession
        DBSession.remove()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Basic Functionality' in res.body)
        #pp.pprint(res.body)
