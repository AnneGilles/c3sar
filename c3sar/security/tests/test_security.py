import unittest

from pyramid import testing


class TestRequestWithUserAttribute(unittest.TestCase):
    """
    This integration test should test the user attribute of a request,
    aimed at coverage...
    maybe I try to just access request.user in another test!?!
    """

    #     def _getTargetClass(self):
    #         from c3sar.security.request import RequestWithUserAttribute
    #         return RequestWithUserAttribute
    #     def _callFUT(self):
    #         pass

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

# ToDo:
#     def test_request_user(self):
#         request = testing.DummyRequest()
#         usertest = request.user
#         self.assertEquals(usertest, None, "request.user was not None.")
