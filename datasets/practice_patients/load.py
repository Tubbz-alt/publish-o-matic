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

def load_pp():
    for directory, metadata_file, metadata in datasets():
        resources = [
            dict(
                description=r['description'],
                name=r['name'],
                format=r['filetype'].upper(),
                url=r['url'],
                url_type='',
            )
            for r in metadata['sources']
        ]
        slug = slugify.slugify(metadata['title']).lower()
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
            frequency=metadata['frequency'],
            extras=[
                #dict(key='coverage_start_date', value=metadata['coverage_start_date']),
                #dict(key='coverage_end_date', value=metadata['coverage_end_date']),
                #dict(key='frequency', value=metadata['frequency']),
                dict(key='publication_date', value=metadata['publication_date'])
            ]
        )
    return


def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    dc.ensure_publisher('hscic')
    load_pp()
    return 0
