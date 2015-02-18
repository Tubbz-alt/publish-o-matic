"""
Make transformations/adjustments/reorganisations of the ODS data
"""
import datetime
import json
import sys

import ffs
import re

from publish.lib.helpers import filename_for_resource, download_file
from publish.lib.upload import Uploader

DATA_DIR = None

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    metadata_file = DATA_DIR / 'dataset.metadata.json'
    datasets = json.load(open(metadata_file, 'r'))

    u = Uploader("ods")
    for dataset in datasets:
        for resource in dataset['resources']:
            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            download_file(resource['url'], path)
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url
    u.close()

    json.dump(datasets, open(metadata_file, 'w'))

