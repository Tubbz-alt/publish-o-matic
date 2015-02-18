import datetime
import json
import sys

import ffs
import re

from publish.lib.helpers import filename_for_resource, download_file
from publish.lib.upload import Uploader


def main(workspace):
    DATA_DIR = ffs.Path(workspace)
    datasets = json.load(open(DATA_DIR / 'ccgois_indicators.json'))

    u = Uploader("ccgois")
    for dataset in datasets:
        resources = []
        for resource in dataset['sources']:
            resource['format'] = resource['filetype']
            resource['name'] = resource['url'].split('/')[-1]

            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            download_file(resource['url'], path)
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url
            resources.append(resource)
        dataset['resources'] = resources
    u.close()

    json.dump(datasets, open(DATA_DIR / 'ccgois_indicators.json', 'w'))
