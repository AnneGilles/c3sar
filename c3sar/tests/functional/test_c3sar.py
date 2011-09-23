# https://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests

import unittest
import pprint

class FunctionalTests(unittest.TestCase):

    def setUp(self):
        from c3sar import main
        import c3sar
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Pyramid' in res.body)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(res)
        
