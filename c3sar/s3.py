# make connections with our i2 database using s3 protocoll

from boto.s3.connection import (
    S3Connection,
    Location,
    OrdinaryCallingFormat)
from boto.s3.key import Key
from boto.exception import S3CreateError

import ConfigParser
import io
import os

class I2S3():
    """
    connect to i2 using S3 protocoll
    """
    print("This is I2S3")
    calling_format=OrdinaryCallingFormat()

    def get_config_from_settings(self):
        """
        load settings from config file s3.ini 
        """
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        print "-- Does config file s3.ini exist? " + str(
            os.path.isfile('s3.ini'))
        config_file = 's3.ini'
#        config.readfp(io.BytesIO(config_file))
        config.read(config_file)
        print "-- i2.access_key_id: " + config.get(
            "i2", "access_key_id")
        print "-- i2.access_key_secret: " + config.get(
            "i2", "access_key_secret")
        print "-- i2.i2_host: " + config.get("i2", "i2_host")
        print "-- i2.is_secure: " + config.get("i2", "is_secure")
        return config

    def __init__(self):
        """set it up, create connection"""
        print("This is I2S3.__init__()")

        try:
            print "getting config from s3.ini"
            self.config = self.get_config_from_settings()
            print str(self.config)
        except Exception, e:
            print "something went wrong. "
            print e


        try:
            self.conn = S3Connection(
                aws_access_key_id = self.config.get("i2", "access_key_id"),
                aws_secret_access_key = self.config.get("i2", "access_key_secret"),
                port = 8091,
                host = self.config.get("i2", "i2_host"),
                calling_format = self.calling_format,
                path = "/",
                is_secure = False # self.config.get("i2", "is_secure")
                )
            print("connection established!!")
        except Exception, e:
            print("connection failed !!!")
            print e
            self.conn = None

    def _get_all_buckets(self):
        """for testing: get all buckets"""
        rs = self.conn.get_all_buckets()
        print "All buckets: ", rs

    def get_all_keys(self):
        """for testing: get all buckets"""
        rs = self.conn.get_all_keys()
        print "All buckets: ", rs

    def create_or_get_bucket(self):
        try:
            bucket = self.conn.create_bucket("c3salpha")
            print("I2S3.create_or_get_bucket(): created bucket: " +  str(bucket))
        except S3CreateError, e:
            print e
            bucket = self.conn.get_bucket("c3salpha")
            print("I2S3.create_or_get_bucket(): got bucket: " + str(bucket))
        return bucket

    def create_named_bucket(self, name):
        bucket = self.conn.create_bucket(name)
        print("I2S3.create_named_bucket(): created bucket " + name)



def initialize_s3():
    print "initialize_s3():"
    i2 = I2S3()
    bucket = i2.create_or_get_bucket()
    print dir(bucket)
    print type(bucket)

    rs = bucket.get_all_keys()
    print "bucket.get_all_keys(): " + str(rs)

    k = Key(bucket)
    k.key = 'foobar'
    k.set_contents_from_string('foobar contains a string')
    k.set_acl('public-read')
    #print k.get_acl()

    rs = bucket.get_all_keys()
    print "bucket.get_all_keys(): " + str(rs)





    #print "dir(i2): " + str(dir(i2))
    #print "type(i2.conn): " + str(type(i2.conn))
    #print "dir(i2.conn): " + str(dir(i2.conn))
    
    #rs = i2.conn.get_all_buckets()
    #print "All buckets: ", rs
    #print ("==================")
    print "i2.conn.is_secure: " + str(i2.conn.is_secure)
    #print "i2.conn.get_all_buckets(): " + str(i2.conn.get_all_buckets())
    #print "i2.conn.create_bucket('testing'): " + str(i2.conn.create_bucket('testing'))
    print "i2.conn.server_name(): " + str(i2.conn.server_name())
    print "i2.conn.get_canonical_user_id(): " + str(i2.conn.get_canonical_user_id())
    print "initialize_s3: done."

