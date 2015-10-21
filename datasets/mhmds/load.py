"""
Load the ASCODF datasets into a CKAN instance
"""
import sys

import dc
import ffs
import slugify

DATA_DIR = None

def datasets():
    for directory in DATA_DIR.ls():
        metadata = directory/'dataset.metadata.json'
        yield directory, metadata, metadata.json_load()

def load_datasets():
    for directory, metadata_file, metadata in datasets():
        resources = [
            dict(
                description=r['description'],
                name=r['url'].split('/')[-1],
                format=r['format'],
                url=r['url']
                #upload=open(str(directory/r['url'].split('/')[-1]), 'r')
            )
            for r in metadata['resources']
        ]
        slug = slugify.slugify(metadata['title']).lower()
        if len(slug) >= 100:
            slug = slug[:99]
        print 'Creating', metadata['title'], slug
        dc.Dataset.create_or_update(
            name=slug,
            title=metadata['title'],
            state='active',
            license_id='uk-ogl',
            notes=metadata['summary'],
            origin=metadata['source'],
            tags=dc.tags(*metadata['tags']),
            resources=resources,
            owner_org='hscic',
            extras=[
                # dict(key='coverage_start_date', value=metadata['coverage_start_date']),
                # dict(key='coverage_end_date', value=metadata['coverage_end_date']),
                # dict(key='frequency', value=metadata['frequency']),
                dict(key='publication_date', value=metadata['publication_date'])
            ]
        )
    return


def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    dc.ensure_publisher('hscic')
    load_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
