"""
"Scrape" HQIP data from DGU.

The original version of this script was provided by @rossjones
"""
import socket
import sys
import urllib

import ckanapi
from ckanapi.errors import NotFound, ValidationError

from dc import ckan as catalogue
from dc import _org_existsp, Dataset
import ffs

DATA_DIR = None

SOURCE = "http://data.gov.uk"
TARGET_ORGANISATION = "healthcare-quality-improvement-partnership"

dgu =  ckanapi.RemoteCKAN(SOURCE)

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    org = dgu.action.organization_show(id=TARGET_ORGANISATION)

    print "Found {0} datasets on source".format(len(org['packages']))

    for package in org['packages']:
        print "Scraping ", package['title'].encode('utf8')

        dataset_dir = DATA_DIR/package['name']
        dataset_dir.mkdir()
        # Get the dataset from DGU
        dataset = dgu.action.package_show(id=package['name'])

        # Set the new owning organisation
        dataset['owner_org'] = org['name']

        # Some datasets have no resources, and we don't like that any more ...
        if not 'resources' in dataset:
            dataset['resources'] = []

        with dataset_dir:
            for resource in dataset['resources']:
                resource['name'] = resource['description']
                if resource['format'] == "HTML":
                    continue
                if resource['url'].startswith('hhttps'):
                    resource['url'] = resource['url'].replace('hhttps', 'https')

                print 'downloading', resource['url']
                filename = resource['url'].split('/')[-1]
                datafile = dataset_dir/filename
                if datafile:
                    print 'already downloaded file'
                    continue
                try:
                    urllib.urlretrieve(resource['url'], filename)
                except IOError:
                    print 'FTW Larry? We got a socket error :('
                    continue


if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
