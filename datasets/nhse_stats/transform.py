import hashlib
import os
import json

import ffs

from publish.lib.helpers import download_file

def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    datasets = json.load(open(os.path.join(DATA_DIR, "metadata.json"), 'r'))

    tag_list = ["Statistics"]
    for dataset in datasets:
        print "Processing", dataset['name']

        print "..adding tags"
        tags = dataset.get('tags', [])
        for t in tag_list:
            if not t in tags:
                tags.append(t)
        dataset['tags'] = tags

        print "..fetching resources"
        for r in dataset["resources"]:
            name = hashlib.sha224(r['url']).hexdigest()
            target = os.path.join(DATA_DIR, name)
            download_file(r['url'], target)


    json.dump(datasets, open(os.path.join(DATA_DIR, "metadata.json"), 'wb'))

    return 0
