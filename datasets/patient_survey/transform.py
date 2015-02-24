"""
Transformer for the patient survey website at https://gp-patient.co.uk/surveys-and-reports
"""
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

    u = Uploader("gp-survey")

    for dataset in datasets:
        print "Processing", dataset['name']

        print "..fetching resources"
        for resource in dataset["resources"]:
            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            download_file(resource['url'], path)
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url

    u.close()
    json.dump(datasets, open(os.path.join(DATA_DIR, "metadata.json"), 'wb'))

    return 0
