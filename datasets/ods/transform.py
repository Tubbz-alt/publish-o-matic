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
from publish.lib.unzip import Unzipper

DATA_DIR = None

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    metadata_file = DATA_DIR / 'dataset.metadata.json'
    datasets = json.load(open(metadata_file, 'r'))

    u = Uploader("ods")
    unzipper = Unzipper()
    for dataset in datasets:
        has_zip = False

        for resource in dataset['resources']:
            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            download_file(resource['url'], path)
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url

            if resource['format'].upper() == 'ZIP':
                has_zip = True

        if has_zip:
            print "Processing ZIP files in dataset"
            print '*' * 30
            unzipper.unzip(dataset)
            print '*' * 30
    u.close()

    json.dump(datasets, open(metadata_file, 'w'))

