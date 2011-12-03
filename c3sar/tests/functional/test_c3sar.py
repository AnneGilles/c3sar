# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests

import unittest
import pprint
pp = pprint.PrettyPrinter(indent=4)


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.config.include('c3sar')
        from c3sar import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Pyramid' in res.body)
        pp.pprint(res.body)


#     def setUp(self):
#         """ This sets up the application registry with the
#         registrations your application declares in its ``includeme``
#         function.
#         """
#         import c3sar

#         from webtest import TestApp
#         self.testapp = TestApp(app)

#     def test_root(self):
#         res = self.testapp.get('/', status=200)
#         self.failUnless('Pyramid' in res.body)

#         pp.pprint(res)

#     def test_main(self):
#         from c3sar import main
#         app = main({})

#    def test_request_user_attribute(self):
#
#        print "------- request.user: " + str(request.user)


suite = unittest.TestLoader().loadTestsFromTestCase(FunctionalTests)
unittest.TextTestRunner(verbosity=2).run(suite)
