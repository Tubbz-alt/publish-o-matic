"""
Download PHE files
"""
import json
import sys
import urllib

import ffs

HERE = ffs.Path.here()
DATA_DIR = HERE / 'data'
DATA_DIR.mkdir()

PHOF_DATA_FILE = 'http://livews-b.phe.org.uk/GetDataDownload.ashx?pid=19&ati=102&res=19&tem=19&par=E92000001&pds=0&pat=6'

def pull_phof_datasets():
    """
    Scrape and pull PHOF datasets
    """
    dataset = {
        'resources': [{
            'url': PHOF_DATA_FILE,
            'filetype': 'xls',
            'description': 'Public Health Outcomes Framework data'
        }]
    }
    with DATA_DIR:
        urllib.urlretrieve(PHOF_DATA_FILE, 'PHOF.xlsx')
    metadata_file = DATA_DIR/'dataset.metadata.json'
    if metadata_file:
        metadata_file.truncate()
    metadata_file << json.dumps(dataset, indent=2)
    return

def main():
    pull_phof_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main())