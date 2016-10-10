"""
Make transformations/adjustments/reorganisations of the QOF data
"""
import os
import datetime
import json
import sys

import ffs
import re

from publish.lib.helpers import filename_for_resource, download_file
from publish.lib.upload import Uploader


DATA_DIR = None

def get_metadata_file(filename):
    root = os.path.dirname(__file__)
    f = os.path.join(root, os.path.pardir, os.path.pardir, "metadata", filename)
    return os.path.abspath(f)


def add_metadata_to_qof_datasets():
    u = Uploader("nshof")

    f = os.path.join(DATA_DIR, "nhsof_metadata_indicators.json")
    datasets = json.load(open(f))

    for metadata in datasets:
        metadata['tags'] = ['QOF', 'Quality Outcomes Framework']
        title = metadata['title']
        #metadata['frequency'] = 'yearly'
        #metadata['title'] = 'QOF - National Quality Outcomes Framework - {0}-{1}'.format(match.group(1), match.group(2))

        resources = []
        for resource in metadata['sources']:
            resource['format'] = resource['filetype']
            resource['name'] = resource['url'].split('/')[-1]
            resource['url_type'] = ''

            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            download_file(resource['url'], path)
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url
            resources.append(resource)
        metadata['resources'] = resources

    json.dump(datasets, open(os.path.join(DATA_DIR, "nhsof_metadata_indicators.json"), "w"))
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    add_metadata_to_qof_datasets()
    return 0
