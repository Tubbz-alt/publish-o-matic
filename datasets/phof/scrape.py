"""
No longer required/used
"""
import json
import sys
import urllib

import ffs

DATA_DIR = None

PHOF_DATA_FILE = 'http://livews-b.phe.org.uk/GetDataDownload.ashx?pid=19&ati=102&res=19&tem=19&par=E92000001&pds=0&pat=6'

def pull_phof_datasets():
    """
    Scrape and pull PHOF datasets
    """
    dataset = {
        'resources': [{
            'name': "PHOF.xlsx",
            'url': PHOF_DATA_FILE,
            'format': 'XLS',
            'description': 'Public Health Outcomes Framework data'
        }]
    }
    metadata_file = DATA_DIR/'dataset.metadata.json'
    if metadata_file:
        metadata_file.truncate()
    metadata_file << json.dumps(dataset, indent=2)
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    pull_phof_datasets()
    return 0
