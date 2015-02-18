"""
Make transformations/adjustments/reorganisations of the ASCOF data
"""
import datetime
import json
import sys

import ffs
import re

from publish.lib.helpers import filename_for_resource, download_file
from publish.lib.upload import Uploader


DATA_DIR = None

def datasets():
    for directory in DATA_DIR.ls():
        metadata = directory/'dataset.metadata.json'
        yield directory, metadata, metadata.json_load()

def add_metadata_to_ascof_datasets():
    for directory, metadata_file, metadata in datasets():
        metadata['tags'] = ['ASCOF', 'Adult Social Care Outcomes Framework']
        title = metadata['title']
        match = re.search('(\d{4})-(\d{2})', title)
        begins = datetime.date(year=int(match.group(1)), month=4, day=1)
        ends = datetime.date(begins.year + 1, 3, 31)
        metadata['coverage_start_date'] = begins.isoformat()
        metadata['coverage_end_date'] = ends.isoformat()
        metadata['frequency'] = 'yearly'
        metadata['title'] = 'ASCOF - Adult Social Care Outcomes Framework, England -{0}-{1}'.format(match.group(1), match.group(2))

        u = Uploader("ascof")
        for resource in metadata['resources']:
            print resource['url']
            filename = filename_for_resource(resource)
            path = directory / filename

            download_file(resource['url'], path)
            print "Uploading to S3"
            url = u.upload(path)
            resource['url'] = url
            print resource['url']
        u.close()

        metadata_file.truncate()
        metadata_file << json.dumps(metadata, indent=2)
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    add_metadata_to_ascof_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))







