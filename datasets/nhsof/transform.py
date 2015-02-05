"""
Make transformations/adjustments/reorganisations of the QOF data
"""
import datetime
import json
import sys

import ffs
import re

HERE = ffs.Path.here()
DATA_DIR = HERE / 'data'

def datasets():
    for directory in DATA_DIR.ls():
        metadata = directory/'dataset.metadata.json'
        yield directory, metadata, metadata.json_load()    

def add_metadata_to_qof_datasets():
    for directory, metadata_file, metadata in datasets():
        metadata['tags'] = ['QOF', 'Quality Outcomes Framework']
        title = metadata['title']
        match = re.search('(\d{4})-(\d{2})', title)
        begins = datetime.date(year=int(match.group(1)), month=4, day=1)
        ends = datetime.date(begins.year + 1, 3, 31)
        metadata['coverage_beginning_date'] = begins.isoformat()
        metadata['coverage_ending_date'] = ends.isoformat()
        metadata['frequency'] = 'yearly'
        metadata['title'] = 'QOF - National Quality Outcomes Framework - {0}-{1}'.format(match.group(1), match.group(2))

        metadata_file.truncate()
        metadata_file << json.dumps(metadata, indent=2)
    return
        
def main():
    add_metadata_to_qof_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main())







