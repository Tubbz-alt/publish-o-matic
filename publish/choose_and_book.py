"""
Publish Choose & Book data
"""
import sys

import ffs

import dc

DATA_DIR = ffs.Path.here()/'../data/'

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

def publish_choose_and_book():
    """
    Do Useful Work Here
    """
    metadatafile = DATA_DIR/'choose.and.book.json'
    metadata = metadatafile.json_load()
    for dataset in metadata:
        resources = [
            dict(
                description=s['description'],
                name=s['description'],
                format=s['filetype'],
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
            url='http://www.chooseandbook.nhs.uk/staff/bau/reports',
            tags=dc.tags(*dataset['tags']),
            resources=resources,
            owner_org=''
        )
    return 
        
def main():
    dc.ensure_publisher('choose-and-book')
    publish_choose_and_book()
    return 0

if __name__ == '__main__':
    sys.exit(main())
