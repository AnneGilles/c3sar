# -*- coding: utf-8 -*-

import unittest
from boto.s3.connection import (
    S3Connection,
    OrdinaryCallingFormat
    )
from boto.exception import S3PermissionsError

#from pyramid import testing

# def _s3_init():
#     from c3sar.s3 import initialize_s3
#     return initialize_s3

class I2s3_Init_Test(unittest.TestCase):
    # testing 23-36
#    from c3sar.s3 import I2S3
#    i2conn = I2S3().conn
    pass

# also test the exception to be thrown...


#     print "This is class I2S3Test."

#     def setUp(self):
#         print "This is class I2S3Test.setUp()"
#         _s3_init()


#     def tearDown(self):
#         print "This is class I2S3Test.tearDown()"
#         pass


#     def test_it(self):
#         print "This is class I2S3Test.testIt()"
#         conn = i2.conn
#         conn.get_all_buckets()

class S3VersioningTest(unittest.TestCase):
    # versioning will be implemented in i2 in about two weeks
    # christoph @tue, sept 13 2011
    pass


if __name__ == '__main__':
    unittest.main()
