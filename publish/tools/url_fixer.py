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
import slugify

import boto.s3.key as s3key
import boto.s3.connection as s3connection
import ffs
import ckanapi

from publish.lib.manifest import get_scraper_names

RESOURCES = ["013ae123-f05f-4a73-9806-b16f3e925c32", "04a2e903-8114-4037-bac1-480c6cdeb32e","0a873564-0a18-4edc-b7e8-5cadc40eecec",
"1e653985-8598-42b7-aefa-8db9122dbae4", "1eaaf9d4-fca2-4c7c-9c00-e2c223430a64", "212b6adb-3196-4854-af7d-1f146a2d3ec9",
"215f73ee-41b3-40fa-8ea7-b6d13f1337ec", "27031f95-dc3b-4874-b25a-e2c2e7402cc4",
"29674e39-589b-4d89-aca3-fb12f120f895", "2c6daf45-eb12-47c6-ab83-100bbdfbb413",
"32a57fe6-c29a-4000-bb7b-7026df930a98", "334e87c4-3060-4bb0-9517-8eedf47e3523",
"434ee817-f6f2-419c-be5f-2d4629e05a69", "44e582af-d838-4fc4-a39a-231bcc2770d9",
"4a7905f9-9461-4a38-9b32-e3f2eeaae756", "4aa9d478-5e08-4086-bd56-5781df2f200f",
"5a621b1a-4e49-4a5a-8cbd-2fad43ef139d",
"5aa31d25-4161-43f4-b091-7f1a56cc690b", "5d9308b6-4a8c-4d80-88a0-c85ec2392a8d",
"67fbde94-a46a-4843-b60e-d66fa63e41eb", "6ec9b5f0-c6e6-4bdb-afef-8956468ecf85", "8f5cd034-9219-45ad-bfdd-49aa6541ccc5",
"90035b42-d2b3-405f-9d63-3e0455cf2e05", "982c5943-e3f3-48f8-bd85-84e0c6c608f0", "a07a2b4f-277f-46fe-9e5a-b13991b03faa",
"a5594295-26a5-4d79-a00a-41f38e867b1e","a70defff-b6d2-4d36-9486-d4d0eba99a10", "ad7d4ce2-a8b1-4fc5-8b5e-ce5394423986",
"afb3049d-78f6-4048-9a4e-6638d2688e0d", "b3c83e2b-3e86-4179-a960-f6b6e726f19f", "b44fd4e7-fdc7-4a70-8a66-c2e5a078c44d",
"ba2fcfae-4d97-4b95-a8d2-81be857add66", "bbed9698-57a7-4c10-a2d1-aacc176727ad", "c36b3b07-2845-4fac-87b6-bf6819457459", "c51f2ae6-7950-419b-bb4b-5d8fca5b0c84",
"cee5f646-0fa5-40fb-8484-3ebcb5effd53", "d07d271c-5933-4eb2-a70b-ef7551563269", "d16afb5b-2575-4068-a4c5-be04c966f543",
"dadfd925-f491-46f3-92c1-f84959325969", "e01fc8b5-6c9b-4a56-9063-4b170cc97dee","e560de1c-8a06-49a6-969c-11535c3ef2e6",
"e6d5b531-2572-48b6-9689-e17461240bce", "f075e75a-387e-4f36-8514-fc662507d3da", "f0b07d1e-910f-42da-a875-91478ff5c415", "f3142c2e-ffa3-42d3-a733-97d88228e4a1",]

import boto.s3.key as s3key
import boto.s3.connection as s3connection

def main():
    """
    Finds all the metadata .json files and builds a list of the URLs.  Will
    then try and copy them using the filename of the URL rather than the hash
    """
    c = ConfigParser.ConfigParser()
    c.read(ffs.Path('~/.dc.ini').abspath)
    bucket_name = c.get('ckan', 'aws_bucket')
    conn = s3connection.S3Connection(c.get('ckan', 'aws_access_key'),
                                          c.get('ckan', 'aws_secret_key'))
    bucket = conn.get_bucket(bucket_name)

    print "Server is ", c.get('ckan', 'url')
    ckan = ckanapi.RemoteCKAN(c.get('ckan', 'url'),
                              apikey=c.get('ckan', 'api_key'))

    active = 0
    """
    res = ckan.action.resource_search(query="url_type:upload")
    for r in res['results']:
        if 'download' in r['url']:
            rid = r['id']
            print rid
            key = u'/{}/{}/{}/{}'.format(
                rid[0:3], rid[3:6], rid[6:], r['url'].split('/')[-1]
            )

            k = s3key.Key(bucket)
            k.key = key
            k.set_acl('public-read')

            if r['url'].split('/')[-1] == 'upload':
                # need to rename the upload to the resource name
                try:
                    new_key = u'/{}/{}/{}/{}'.format(
                        rid[0:3], rid[3:6], rid[6:], slugify.slugify(r['name']) + "." + r['format'].lower()
                    )

                    xk = s3key.Key(bucket)
                    xk.key = new_key
                    if not xk.exists():
                        print new_key, "does not exist"
                        print " ... updating S3 file ... "
                        blob = k.get_contents_as_string()
                        xk.set_contents_from_string(blob)
                        xk.set_acl('public-read')

                    key = new_key
                except Exception, e:
                    import time
                    time.sleep(5)

                    print "Copy failed"
                    print e

            r['url_type'] = ''
            r['url'] = "https://nhsenglandfilestore.s3.amazonaws.com{}".format(key)

            print "Updating CKAN resource ---"
            try:
                ckan.action.resource_update(**r)
            except:
                print "Failed to process resource id ", r['id']
                continue

    """
    for r in RESOURCES:
        print r
        resource = ckan.action.resource_show(id=r)
        print resource['id'], resource['datastore_active']
        #res = ckan.action.datapusher_submit(resource_id=r, ignore_hash=True)
        #print res

if __name__ == "__main__":
    main()