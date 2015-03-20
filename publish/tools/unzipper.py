#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This tool is used to find .zip files on a CKAN instance and then:

    1. Pull the .zip
    2. Extract the contents
    3. Re-upload as new resources if they themselves are not .zips
    4. Delete the original .zip

'''
import ConfigParser
import os
from urlparse import urljoin
import shutil
import sys
import tempfile
import zipfile

import ckanapi
import ffs
import requests
import requests_cache

config = ConfigParser.ConfigParser()
config.read(ffs.Path('~/.dc.ini').abspath)


class Unzipper(object):

    def __init__(self, ckan):
        self.ckan = ckan

    def unzip(self):
        packages = []
        total = 0
        while len(packages) <= 9: #total:
            print " -- Calling package_search"

            res = requests.get(urljoin(config.get('ckan', 'url'), 'api/3/action/package_search'),
                params={"q":".zip", "start": len(packages), "rows":10})
            data = res.json()['result']
            total += data['count']
            packages.extend(data['results'])
            print "Fetched info on {} of {}".format(len(packages), data['count'])

        print "Found {} packages with zips".format(data['count'])
        for pkg in packages:
            self.process_package(pkg)

    def process_package(self, package):
        print " +", package['name']
        for resource in package['resources']:
            if not resource['format'] == 'ZIP':
                continue
            print "   +", resource['name']
            extract_zip_to = self.unzip_file(resource['url'])
            print "        + Processing files in ", extract_zip_to

            shutil.rmtree(extract_zip_to)

    def unzip_file(self, url):
        """
        Fetches a file from a url, unzips it and returns the folder
        where the files were unzipped
        """
        download_file_to, filename = tempfile.mkstemp()
        extract_zip_to = tempfile.mkdtemp()

        r = requests.get(url, stream=True)
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                os.write(download_file_to, chunk)

        os.close(download_file_to)

        zip = zipfile.ZipFile(filename)
        for info in zip.infolist():
            zip.extract(info.filename, extract_zip_to)
        zip.close()
        print "        + Extracted {} files".format(len(zip.infolist()))

        os.unlink(filename)
        return extract_zip_to




def main():
    requests_cache.install_cache('unzipper_cache', expire_after=82400)

    print "Server is ", config.get('ckan', 'url')
    ckan = ckanapi.RemoteCKAN(config.get('ckan', 'url'),
                              apikey=config.get('ckan', 'api_key'))
    unzipper = Unzipper(ckan)
    unzipper.unzip()

