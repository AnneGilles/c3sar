# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests

import unittest
import pprint
pp = pprint.PrettyPrinter(indent=4)


class FunctionalTests(unittest.TestCase):

    def setUp(self):
#        from c3sar.models import DBSession
#        global dbsession
#        self.dbsession = DBSession
#        self.dbsession.remove()
        from c3sar import main
        my_settings = {'sqlalchemy.url': 'sqlite://'}  # mock
#        from sqlalchemy import create_engine
#        engine = create_engine('sqlite://')
        from sqlalchemy import engine_from_config
        engine = engine_from_config(my_settings)
        app = main({}, **my_settings)
        # if I try app = main({}) it tells me 'url' wasnt there
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Basic Functionality' in res.body)
        #pp.pprint(res.body)
