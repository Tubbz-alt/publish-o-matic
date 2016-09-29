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

    tag_list = ["Statistics"]
    u = Uploader("stats")

    for dataset in datasets:
        print "Processing", dataset['name']

        print "..adding tags"
        tags = dataset.get('tags', [])
        for t in tag_list:
            if not t in tags:
                tags.append(t)
        dataset['tags'] = tags

        print "..fetching resources"
        for resource in dataset["resources"]:
            filename = filename_for_resource(resource)
            path = DATA_DIR / filename

            try:
                download_file(resource['url'], path)
            except:
                continue
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url
            resource['url_type'] = ''  # make sure we zap historical uploads

    json.dump(datasets, open(os.path.join(DATA_DIR, "metadata.json"), 'wb'))

    return 0
