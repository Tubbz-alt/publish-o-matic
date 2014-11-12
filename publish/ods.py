"""
Publish scraped ODS data to a CKAN instance
"""
import sys

import ffs

import dc

DATA_DIR = ffs.Path.here()/'../data/'

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

def publish_ods():
    """
    Do Useful Work Here
    """
    metadatafile = DATA_DIR/'ods.json'
    metadata = metadatafile.json_load()
    for dataset in metadata:
        resources = [
            dict(
                description=s['description'],
                name=s['description'],
                format=dc.filetype(s['url']),
                upload=dc.disk_fh_for_url(s['url'])          
            )
            for s in dataset['resources']
        ]
        dc.Dataset.create_or_update(
            name=dataset['title'].lower().replace(' ', '-'),
            title=dataset['title'],
            state='active',
            licence_id='ogl',
            notes=dataset['description'],
            url='http://systems.hscic.gov.uk/data/ods',
            tags=dc.tags('ODS', 'Organisation', 'Organization'),
            resources=resources,
            owner_org='hscic-ods'
        )
    return 
        
def main():
    dc.ensure_publisher('hscic-ods')
    publish_ods()
    return 0

if __name__ == '__main__':
    sys.exit(main())
