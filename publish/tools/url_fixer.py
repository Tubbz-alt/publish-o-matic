#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Fixes URLs from the hashed name, and copies them to the proper name
'''
import collections
import ConfigParser
import hashlib
import json
import os
import sys
import time

import boto.s3.key as s3key
import boto.s3.connection as s3connection
import ffs
import ckanapi

from publish.lib.manifest import get_scraper_names

def read_resources(dataset):
    if ('resources' not in dataset) and ('sources' not in dataset):
        return []
    l = dataset.get('resources', dataset.get('sources'))
    return [r['url'] for r in l]

def get_urls_from_file(file):
    urls = []

    obj = json.load(open(file, 'r'))
    if isinstance(obj, dict):
        urls.extend(read_resources(obj))
    else:
        for dataset in obj:
            urls.extend(read_resources(dataset))

    return filter(lambda x: x is not None, urls)

def walk(arg, dirname, names):
    path = dirname.split('/')
    if len(path) < 3:
        return

    key = path[2]
    if not key in get_scraper_names():
        return

    if key == 'patient_survey':
        key = 'gp-survey'
    if key == 'nhse_stats':
        key = 'stats'

    # TODO: Remove this once we've worked out what to do with the relevant json
    if key == 'hscic':
        return

    json_files = [n for n in names if n.endswith('json')]
    if not json_files:
        return

    urls = []
    for f in json_files:
        urls = get_urls_from_file(os.path.join(dirname,f))
        print key, len(urls)
        arg[key].extend(urls)

def main():
    """
    Finds all the metadata .json files and builds a list of the URLs.  Will
    then try and copy them using the filename of the URL rather than the hash
    """
    files = collections.defaultdict(list)
    os.path.walk("/tmp", walk, files)

    c = ConfigParser.ConfigParser()
    c.read(ffs.Path('~/.dc.ini').abspath)

    print "Server is ", c.get('ckan', 'url')
    ckan = ckanapi.RemoteCKAN(c.get('ckan', 'url'),
                              apikey=c.get('ckan', 'api_key'))


    output = {}
    count = 0
    for name, urls in files.iteritems():
        for url in sorted(urls):
            print count
            count = count + 1
            hashed = hashlib.md5(url.encode('utf8')).hexdigest()
            ext = url.encode('utf8').split('.')[-1]

            old_url = "{}/{}.{}".format(name, hashed, ext)

            try:
                new_url = u"{}/{}".format(name.encode('latin1'), url.encode('utf8').split('/')[-1])
            except:
                continue

            old = "https://nhsenglandfilestore.s3.amazonaws.com/{}".format(old_url)
            new = "https://nhsenglandfilestore.s3.amazonaws.com/{}".format(new_url)
            output[old] = new

            print "Looking for ", old
            r = ckan.action.resource_search(query="url:{}".format(old))
            if r['count'] == 0:
                continue

            for resource in r['results']:
                print resource['name']
                resource['url'] = new
                try:
                    ckan.action.resource_update(**resource)
                    print "Updated ...", resource['id']
                except Exception, e:
                    print "Failed to update .... might need to do this manually"
                    print e
                    import sys; sys.exit(0)



    """
    This copied all of the old URLs to the new location for each
    bucket_name = c.get('ckan', 'aws_bucket')
    conn = s3connection.S3Connection(c.get('ckan', 'aws_access_key'),
                                          c.get('ckan', 'aws_secret_key'))
    bucket = conn.get_bucket(bucket_name)

    for name, urls in files.iteritems():
        for url in urls:
            hashed = hashlib.md5(url.encode('utf8')).hexdigest()
            ext = url.encode('utf8').split('.')[-1]

            old_url = "{}/{}.{}".format(name, hashed, ext)

            try:
                new_url = u"{}/{}".format(name.encode('latin1'), url.encode('utf8').split('/')[-1])
            except:
                continue

            print "Copying {} to {}".format(old_url, new_url)
            k = s3key.Key(bucket)
            k.key = old_url
            try:
                k.copy(bucket_name, new_url)
            except:
                print " ... old_url doesn't exist!"

            time.sleep(0.5)
            print "... done"

     #

    conn.close()
    """