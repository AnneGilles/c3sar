# -*- coding: utf-8 -*-
# Copyright (c) 2006-2011 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

# taken from
# https://github.com/boto/boto/blob/master/tests/s3/test_connection.py
# Tue Sept 13 2011
# and adapted for our purpose

import unittest
import time
import os
import urllib
from boto.s3.connection import (
    S3Connection,
    OrdinaryCallingFormat
    )
from boto.exception import S3PermissionsError


class S3ConnectionTest (unittest.TestCase):

    my_aws_access_key_id = "c3salpha"
    my_aws_secret_access_key = "CHANGE_ME"
    my_s3_host = "storage.i2.io"
    calling_format = OrdinaryCallingFormat()

    def off_test_1_basic(self):
        print '--- running S3Connection tests ---'
        c = S3Connection(
            aws_access_key_id=self.my_aws_access_key_id,
            aws_secret_access_key=self.my_aws_secret_access_key,
            port=8091,
            host=my_s3_host,
            calling_format=self.calling_format,
            path="/",
            is_secure=False)
        # create a new, empty bucket
        bucket_name = 'test-%d' % int(time.time())
        print "the bucket_name is: " + bucket_name
        bucket = c.create_bucket(bucket_name)
        # now try a get_bucket call and see if it's really there
        bucket = c.get_bucket(bucket_name)
        # test logging
        logging_bucket = c.create_bucket(bucket_name + '-log')
        logging_bucket.set_as_logging_target()
        bucket.enable_logging(
            target_bucket=logging_bucket,
            target_prefix=bucket.name)
        bucket.disable_logging()
#        c.delete_bucket(logging_bucket)
        k = bucket.new_key()
        k.name = 'foobar'
        s1 = 'This is a test of file upload and download'
        s2 = 'This is a second string to test file upload and download'
        k.set_contents_from_string(s1)
        fp = open('foobar', 'wb')
        # now get the contents from s3 to a local file
        k.get_contents_to_file(fp)
        fp.close()
        fp = open('foobar')
        # check to make sure content read from s3 is identical to original
        assert s1 == fp.read(), 'corrupted file'
        fp.close()
        # test generated URLs
        url = k.generate_url(3600)
        file = urllib.urlopen(url)
        assert s1 == file.read(), 'invalid URL %s' % url
        url = k.generate_url(3600, force_http=True)
        file = urllib.urlopen(url)
        assert s1 == file.read(), 'invalid URL %s' % url
        url = k.generate_url(3600,
                             force_http=True,
                             headers={'x-amz-x-token': 'XYZ'})
        file = urllib.urlopen(url)
        assert s1 == file.read(), 'invalid URL %s' % url
#        bucket.delete_key(k)
        # test a few variations on get_all_keys - first load some data
        # for the first one, let's override the content type
        phony_mimetype = 'application/x-boto-test'
        headers = {'Content-Type': phony_mimetype}
        k.name = 'foo/bar'
        k.set_contents_from_string(s1, headers)
        k.name = 'foo/bas'
        k.set_contents_from_filename('foobar')
        k.name = 'foo/bat'
        k.set_contents_from_string(s1)
        k.name = 'fie/bar'
        k.set_contents_from_string(s1)
        k.name = 'fie/bas'
        k.set_contents_from_string(s1)
        k.name = 'fie/bat'
        k.set_contents_from_string(s1)
        # try resetting the contents to another value
        md5 = k.md5
        k.set_contents_from_string(s2)
        assert k.md5 != md5
#        os.unlink('foobar')
        all = bucket.get_all_keys()
        assert len(all) == 6
        rs = bucket.get_all_keys(prefix='foo')
        assert len(rs) == 3
        rs = bucket.get_all_keys(prefix='', delimiter='/')
        assert len(rs) == 2
        rs = bucket.get_all_keys(maxkeys=5)
        assert len(rs) == 5
        # test the lookup method
        k = bucket.lookup('foo/bar')
        assert isinstance(k, bucket.key_class)
        assert k.content_type == phony_mimetype
        k = bucket.lookup('notthere')
        assert k == None
        # try some metadata stuff
        k = bucket.new_key()
        k.name = 'has_metadata'
        mdkey1 = 'meta1'
        mdval1 = 'This is the first metadata value'
        k.set_metadata(mdkey1, mdval1)
        mdkey2 = 'meta2'
        mdval2 = 'This is the second metadata value'
        k.set_metadata(mdkey2, mdval2)
        # try a unicode metadata value
        mdval3 = u'föö'
        mdkey3 = 'meta3'
        k.set_metadata(mdkey3, mdval3)
        k.set_contents_from_string(s1)
        k = bucket.lookup('has_metadata')
        assert k.get_metadata(mdkey1) == mdval1
        assert k.get_metadata(mdkey2) == mdval2
        assert k.get_metadata(mdkey3) == mdval3
        k = bucket.new_key()
        k.name = 'has_metadata'
        k.get_contents_as_string()
        assert k.get_metadata(mdkey1) == mdval1
        assert k.get_metadata(mdkey2) == mdval2
        assert k.get_metadata(mdkey3) == mdval3
#        bucket.delete_key(k)
        # test list and iterator
        rs1 = bucket.list()
#        print rs1
        num_iter = 0
        for r in rs1:
            num_iter = num_iter + 1
        rs = bucket.get_all_keys()
        print "bucket.get_all_keys()" + str(rs)


if __name__ == '__main__':
    unittest.main()
