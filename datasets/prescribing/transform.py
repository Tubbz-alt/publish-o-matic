"""
Make transformations/adjustments/reorganisations of the Prescribing data
"""
import datetime
import json
import sys

import ffs
import re

DATA_DIR = None

def datasets():
    metadata = DATA_DIR / 'dataset.metadata.json'
    return metadata.json_load()

def add_metadata_to_qof_datasets():
    results = []
    for metadata in datasets():
        metadata['tags'] = ['QOF', 'Quality Outcomes Framework']
        title = metadata['title']
        match = re.search('(\d{4})-(\d{2})', title)
        begins = datetime.date(year=int(match.group(1)), month=4, day=1)
        ends = datetime.date(begins.year + 1, 3, 31)
        metadata['coverage_start_date'] = begins.isoformat()
        metadata['coverage_end_date'] = ends.isoformat()
        metadata['frequency'] = 'yearly'
        metadata['title'] = 'QOF - National Quality Outcomes Framework - {0}-{1}'.format(match.group(1), match.group(2))

        results.append(metadata)

    f = DATA_DIR / 'dataset.metadata.json'
    json.dump(results, open(f, 'w'))

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    add_metadata_to_qof_datasets()
    return 0

