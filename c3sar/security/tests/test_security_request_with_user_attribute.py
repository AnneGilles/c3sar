# import unittest
# from pyramid import testing

# class TestRequestWithUserAtribute(unittest.TestCase):

#     def setUp(self):
#         self.config = testing.setUp()

#     def teatDown(self):
#         testing.tearDown()

#     def test_it(self):
#         request = testing.DummyRequest()
#         usertest = request.user.username

#        print "-- request.user.username: " + str(usertest)

#        from c3sar.security.request import RequestWithUserAttribute
#        from pyramid.decorator import reify
#        usertest = RequestWithUserAttribute.user
#        #print str(dir(usertest))
#        print "-- str(usertest): " + str(usertest) 
#        print "-- type(usertest): " + str(type(usertest))
#        self.assertEqual(type(usertest),"<class 'pyramid.decorator.reify'>", "wrong type!")
#        self.assertTrue(isinstance(usertest,pyramid.decorator.reify))
    
