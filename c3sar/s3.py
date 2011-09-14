# make connections with our i2 database using s3 protocoll

from boto.s3.connection import (
    S3Connection,
    Location,
    OrdinaryCallingFormat)
from boto.s3.key import Key


class I2S3():
    """
    connect to i2 using S3 protocoll
    """
    print("This is I2S3")
    my_aws_access_key_id = "c3salpha"
    my_aws_secret_access_key = "CHANGE_ME"
    calling_format=OrdinaryCallingFormat()
    my_s3_host = "storage.i2.io"

    def __init__(self):
        """set it up, create connection"""
        print("This is I2S3.__init__()")

        try:
            self.conn = S3Connection(aws_access_key_id = self.my_aws_access_key_id,
                                aws_secret_access_key = self.my_aws_secret_access_key,
                                port = 8091,
                                host = self.my_s3_host,
                                calling_format = self.calling_format,
                                path = "/",
                                is_secure = False)
            print("connection established!!")
        except Exception, e:
            print("connection failed !!!")
            print e

    def getAllBuckets(self):
        """for testing: get all buckets"""
        rs = self.conn.get_all_buckets()
        print "All buckets: ", rs

    def create_bucket(self):
        bucket = self.conn.create_bucket("c3sbucket")
        print("I2S3.create_bucket(): created bucket ")
        print(bucket)

    def create_named_bucket(self, name):
        bucket = self.conn.create_bucket(name)
        print("I2S3.create_named_bucket(): created bucket " + name)



def initialize_s3():
    print "initialize_s3():"
    i2 = I2S3()
    bucket = i2.conn.get_bucket('c3salpha')
    k = Key(bucket)
    k.key = 'foobar'
    k.set_contents_from_string('foobar contains a string')
    k.set_acl('public-read')
    #print "dir(i2): " + str(dir(i2))
    #print "type(i2.conn): " + str(type(i2.conn))
    #print "dir(i2.conn): " + str(dir(i2.conn))
    
    #rs = i2.conn.get_all_buckets()
    #print "All buckets: ", rs
    #print ("==================")
    #print "i2.conn.is_secure: " + str(i2.conn.is_secure)
    #print "i2.conn.get_all_buckets(): " + str(i2.conn.get_all_buckets())
    #print "i2.conn.create_bucket('testing'): " + str(i2.conn.create_bucket('testing'))
    #print "i2.conn.server_name(): " + str(i2.conn.server_name())
    #print "i2.conn.get_canonical_user_id(): " + str(i2.conn.get_canonical_user_id())
    print "initialize_s3: done."

