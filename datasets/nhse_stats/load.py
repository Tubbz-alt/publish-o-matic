"""
Load the Statistic datasets into a CKAN instance
"""
import hashlib
import json
import os
import sys

import dc
import ffs



def load_statistic(dataset, directory):
    for r in dataset['resources']:
        hash = hashlib.sha224(r['url']).hexdigest()
        r['upload'] = open(os.path.join(directory, hash), 'r')

    print 'Creating', dataset['title'], dataset['name']
    dc.Dataset.create_or_update(
        name=dataset['name'],
        title=dataset['title'],
        state='active',
        licence_id='ogl',
        notes=dataset['notes'],
        url=dataset['source'],
        tags=dc.tags(*dataset['tags']),
        resources=dataset["resources"],
        owner_org='nhs-england',
        extras=[
            dict(key='coverage_start_date', value=dataset['coverage_start_date']),
            dict(key='coverage_end_date', value=dataset['coverage_end_date']),
            dict(key='frequency', value=dataset['frequency']),
            #dict(key='publication_date', value=metadata['publication_date'])
        ]
    )

def groups(dataset):
    dataset = dc.ckan.action.package_show(id=dataset["name"])
    if [g for g in dataset['groups'] if g['name'].lower() == 'statistics']:
        print 'Already in group', g['name']
    else:
        dc.ckan.action.member_create(
            id='statistics',
            object=dataset['name'],
            object_type='package',
            capacity='member'
        )
    return

def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    dc.ensure_publisher('nhs-england')
    dc.ensure_group('statistics')

    datasets = json.load(open(os.path.join(DATA_DIR, "metadata.json"), "r"))
    for dataset in datasets:
        load_statistic(dataset, DATA_DIR)
        groups(dataset)
