import hashlib
import os
import json

import ffs

from publish.lib.helpers import filename_for_resource, download_file
from publish.lib.upload import Uploader

def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    datasets = json.load(open(os.path.join(DATA_DIR, "metadata.json"), 'r'))
    u = Uploader("staff_survey")

    for dataset in datasets:
        print "Processing", dataset['name']
        print "..fetching resources"
        for resource in dataset["resources"]:
            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            try:
                download_file(resource['url'], path)
                print "Uploading to S3"
                url = u.upload(path)
            except:
                print "Failed to download '{}'".format(url)
                continue
            resource['url'] = url

    json.dump(datasets, open(os.path.join(DATA_DIR, "metadata.json"), 'wb'))

    return 0
