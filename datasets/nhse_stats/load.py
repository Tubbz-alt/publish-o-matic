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
    print 'Creating', dataset['title'].encode('utf8'), dataset['name'].encode('utf8')
    try:
        extras = []
        if dataset.get('coverage_start_date', ''):
            extras.append(dict(key='coverage_start_date', value=dataset['coverage_start_date']))
        if dataset.get('coverage_end_date', ''):
            extras.append(dict(key='coverage_end_date', value=dataset['coverage_end_date']))
        if dataset.get('frequency', ''):
            extras.append(dict(key='frequency', value=dataset['frequency']))

        dc.Dataset.create_or_update(
            name=dataset['name'],
            title=dataset['title'],
            state='active',
            licence_id='ogl',
            notes=dataset['notes'],
            url=dataset['origin'],
            tags=dc.tags(*dataset['tags']),
            resources=dataset["resources"],
            owner_org='nhs-england',
            origin=dataset.get('origin', ''),
            extras=extras,
        )
        return True
    except Exception, e:
        print "ERROR: Problem updating/creating dataset - {}".format(dataset['name'])
        print e

    return False

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
        if load_statistic(dataset, DATA_DIR):
            groups(dataset)
