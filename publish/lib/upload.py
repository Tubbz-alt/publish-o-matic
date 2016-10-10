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
import boto3
import ffs
import requests


class Uploader(object):
    def __init__(self, owner):
        self.owner = owner

        c = ConfigParser.ConfigParser()
        c.read(ffs.Path('~/.dc.ini').abspath)

        self.bucket_name = c.get('ckan', 'aws_bucket')
        self.conn = boto3.resource('s3')
        self.bucket = self.conn.Bucket(self.bucket_name)

    def build_bucket_path(self, local_file):
        filename = local_file.split('/')[-1]
        return "{}/{}".format(self.owner, filename)

    def get_local_hash(self, local_file):
        try:
            return open("{}.hash".format(local_file)).read()
        except:
            print local_file
        return None

    def get_remote_hash(self, local_file):
        """ Gets the remote hash for a file, or None """
        url = self.get_s3_url(local_file)
        h = requests.head(url)
        etag = h.headers.get('etag')
        if not etag:
            return None

        return etag[1:-1]

    def write_file_to_bucket(self, local_file):
        path = self.build_bucket_path(local_file)
        obj = self.conn.Object(self.bucket_name, path)
        with open(local_file, 'rb') as f:
            obj.put(Body=f)
        obj.Acl().put(ACL='public-read')
        return obj

    def get_s3_url(self, local_file):
        return "https://{}.s3.amazonaws.com/{}".format(
            self.bucket_name, self.build_bucket_path(local_file)
        )

    def upload(self, local_file):
        """ Returns the new URL of the uploaded file """
        local_hash = self.get_local_hash(local_file)
        remote_hash = self.get_remote_hash(local_file)
        if not remote_hash or not local_hash == remote_hash:
            self.write_file_to_bucket(local_file)

        return self.get_s3_url(local_file)
