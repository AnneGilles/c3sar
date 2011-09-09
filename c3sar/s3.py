# make connections with our i2 database using s3 protocoll

from boto.s3.connection import (
    S3Connection,
    Location,
    OrdinaryCallingFormat)
from boto.s3.key import Key


def initialize_s3():
    print "initialize_s3():"
    #conn = S3Connection('c3salpha', 'thefuckingpassword')
    conn = I2S3()
    bucket = conn.create_bucket()
    bucket = conn.create_named_bucket('pylonsbook')
    k = Key(bucket)
    k.key = 'foobar'
    k.set_contents_from_filename('foo.png')
    k.get_contents_to_filename('bar.png')



class I2S3():
    """
    connect to i2 using S3 protocoll
    """
    
    my_aws_access_key_id = "c3salpha"
    my_aws_secret_access_key = "thefuckingpassword" # very very secure
    calling_format=OrdinaryCallingFormat()

    try:
        conn = S3Connection(aws_access_key_id = my_aws_access_key_id,
                            aws_secret_access_key = my_aws_secret_access_key,
                            port = 8091,
                            host = "alpha.shri.de",
                            calling_format = calling_format,
                            path = "/",
                            is_secure = False)
    except:
        print("connection failed !!!")


    def __init__(self):
        """set it up, create connection"""
        print("This is I2S3.__init__()")
        conn = self.conn

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

