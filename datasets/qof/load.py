"""
Load the QOF datasets into a CKAN instance
"""
import json
import sys

import ckanapi
import dc
import ffs
import slugify

DATA_DIR = None

def datasets():
    return json.loads(open(DATA_DIR / 'dataset.metadata.json').read())

def load_qof():
    for metadata in datasets():
        resources = [
            dict(
                description=r['description'],
                name=r['name'],
                format=r['format'],
                url=r['url']
            )
            for r in metadata['resources']
        ]
        print 'Creating', metadata['title'], "with {} resources".format(len(metadata['resources']))
        dc.Dataset.create_or_update(
            name=slugify.slugify(metadata['title']).lower(),
            title=metadata['title'],
            state='active',
            licence_id='ogl',
            notes=metadata['summary'],
            url=metadata['source'],
            tags=dc.tags(*metadata['tags']),
            resources=resources,
            owner_org='hscic',
            extras=[
                dict(key='coverage_start_date', value=metadata['coverage_start_date']),
                dict(key='coverage_end_date', value=metadata['coverage_end_date']),
                dict(key='frequency', value=metadata['frequency']),
                dict(key='publication_date', value=metadata['publication_date'])
            ]
        )
        print "... done"
    return

def group_qof():
    remaining = []
    for metadata in datasets():
        dataset_name = slugify.slugify(metadata['title']).lower()
        try:
            dataset = dc.ckan.action.package_show(id=dataset_name)
        except ckanapi.errors.NotFound:
            remaining.append(dataset_name)
            continue

        if [g for g in dataset['groups'] if g['name'].lower() == 'qof']:
            print 'Already in QOF group'

        else:
            dc.ckan.action.member_create(
                id='qof',
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )
    print remaining
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    dc.ensure_publisher('hscic')
    dc.ensure_group('qof')
    load_qof()
    group_qof()
    return 0
