"""
Handles uploading a resource to S3.

Filenames are based on the hash of the url from where the resource
came from, with the extension re-added.

During upload, the following steps are taken, given the filename abc

1. Does abc.hash exist, if so check it against the hash of the current
   file.
2. If the hashes match, abort.
3. Upload both abc and abc.hash to the bucket in a folder
   labelled after the scraper.
4. Return the URL of the newly created file
"""
import ConfigParser
import hashlib
import mimetypes
import os

import boto.s3.key as s3key
import boto.s3.connection as s3connection
import ffs
import requests

class Uploader(object):

    def __init__(self, scraper_name):
        self.scraper_name = scraper_name

        c = ConfigParser.ConfigParser()
        c.read(ffs.Path('~/.dc.ini').abspath)

        self.bucket_name = c.get('ckan', 'aws_bucket')
        self.conn = s3connection.S3Connection(c.get('ckan', 'aws_access_key'),
                                              c.get('ckan', 'aws_secret_key'))
        self.bucket = self.conn.get_bucket(self.bucket_name)


    def close(self):
        self.conn.close()

    def build_bucket_path(self, local_file):
        filename = local_file.split('/')[-1]
        return "{}/{}".format(self.scraper_name, filename)

    def get_local_hash(self, local_file):
        try:
            return open("{}.hash".format(local_file)).read()
        except:
            print local_file
        return None

    def get_remote_hash(self, local_file):
        """ Gets the remote hash for a file, or None """
        url = "https://{}.s3.amazonaws.com/{}".format(self.bucket_name,
                                                       self.build_bucket_path(local_file))
        h = requests.head(url)
        etag = h.headers.get('etag')
        if not etag:
            return None

        return etag[1:-1]

    def write_file_to_bucket(self, local_file):
        path = self.build_bucket_path(local_file)
        print "Writing file", path
        k = s3key.Key(self.bucket)
        k.key = path
        k.set_contents_from_filename(str(local_file))
        k.set_acl('public-read')


    def upload(self, local_file):
        """ Returns the new URL of the uploaded file """
        local_hash = self.get_local_hash(local_file)
        remote_hash = self.get_remote_hash(local_file)
        print local_hash, remote_hash
        if not remote_hash or not local_hash == remote_hash:
            print "Remote_hash is :", remote_hash
            print "Local hash is : ", local_hash
            self.write_file_to_bucket(local_file)
            remote_hash = local_hash

        return "https://{}.s3.amazonaws.com/{}".format(self.bucket_name,
                                                       self.build_bucket_path(local_file))


if __name__ == "__main__":
    from publish.lib.helpers import download_file

    u = Uploader("ods")
    print u.upload("/tmp/ods/data/12345.xls")
    u.close()
