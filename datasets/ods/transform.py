"""
Make transformations/adjustments/reorganisations of the ODS data
"""
import datetime
import json
import sys

import ffs
import re

DATA_DIR = None

def datasets():
    input_file = DATA_DIR/'dataset.metadata.json'
    metadata = input_file.json_load()
    for dataset in metadata:
        directory = DATA_DIR / dataset['name']
        yield directory, input_file, dataset

def add_metadata_to_ods_datasets():
    new_metadata = []

    matcher = re.compile('^(.*)\(.*\)$')

    for directory, metadata_file, metadata in datasets():
        metadata['tags'] = ['ODS', 'Organisation Data Service']
        title = metadata['title']

        metadata['coverage_beginning_date'] = ""
        metadata['coverage_ending_date'] = ""
        metadata['frequency'] = ""
        metadata['title'] = "ODS - {}".format(title)
        metadata['name'] = "ods-{}".format(metadata["name"])

        # Remove (PDF, 14.6kB) from each resource as it is describing the size of the
        # files once pulled out of the .zip
        resources = metadata['resources']
        for r in resources:
            m = matcher.match(r['description'])
            if m:
                r['description'] = m.groups(0)[0]
        new_metadata.append(metadata)

    # Save new metadata
    metadata_file.truncate()
    metadata_file << json.dumps(new_metadata, indent=2)

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    add_metadata_to_ods_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))







