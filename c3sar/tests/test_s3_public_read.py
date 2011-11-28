import unittest
from boto.s3.connection import (
    S3Connection,
    OrdinaryCallingFormat
)
from boto.exception import S3CreateError


class S3PublicReadTest(unittest.TestCase):
    """
    test uploading some file and giving it public read ACL

    can it be downloaded via http?
    """
    my_aws_access_key_id = "c3salpha"
    my_aws_secret_access_key = "CHANGE_ME"
    calling_format = OrdinaryCallingFormat()
    my_bucket_name = "c3salpha"
    my_s3_host = "storage.i2.io"

    def off_test_public_read(self):
        print "--- running public read test ---"
        c = S3Connection(
            aws_access_key_id=self.my_aws_access_key_id,
            aws_secret_access_key=self.my_aws_secret_access_key,
            port=8091,
            host=my_s3_storage,
            calling_format=self.calling_format,
            path="/",
            is_secure=False
            )
        try:
            bucket = c.create_bucket(self.my_bucket_name)
        except S3CreateError, c:
            print "-- got an exception when attempting to create bucket, "
            "trying get_bucket instead"
            #print c
            try:
                bucket = c.get_bucket(self.my_bucket_name)
            except AttributeError, e:
                print "got an AttributeError:"
                print e

        print "--- dir(bucket) ---"
        print dir(bucket)
        print "--- ---"

        print "bucket.get_acl: " + str(bucket.get_acl())
        bucket.set_acl('public-read')
        print "bucket.get_acl: " + str(bucket.get_acl())
        k = bucket.new_key()
        k.name = 'publicFoobar'
        k.key = 'publicFoobar'
        s1 = "I am a teststring."
        k.set_contents_from_string(s1)
        k.set_acl('public-read')
        print "--- done with the public read test ---"

if __name__ == '__main__':
    unittest.main()
