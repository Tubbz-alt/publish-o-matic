"""
Loader for the patient survey website at https://gp-patient.co.uk/surveys-and-reports
"""

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

    extras = []
    if dataset.get('coverage_start_date', ''):
        extras.append(dict(key='coverage_start_date', value=dataset['coverage_start_date']))
    if dataset.get('coverage_end_date', ''):
        extras.append(dict(key='coverage_end_date', value=dataset['coverage_end_date']))

    try:
        dc.Dataset.create_or_update(
            name=dataset['name'],
            title=dataset['title'],
            state='active',
            license_id='uk-ogl',
            notes=dataset['notes'],
            origin=dataset['origin'],
            tags=dc.tags(*dataset['tags']),
            resources=dataset["resources"],
            owner_org='gp-survey',
            extras=extras,
            frequency='Monthly'
        )
        return True
    except Exception, e:
        print "ERROR: Problem updating/creating dataset - {}".format(dataset['name'])
        print e

    return False

def groups(dataset):
    dataset = dc.ckan.action.package_show(id=dataset["name"])
    if [g for g in dataset['groups'] if g['name'].lower() == 'surveys']:
        print 'Already in group', g['name']
    else:
        dc.ckan.action.member_create(
            id='surveys',
            object=dataset['name'],
            object_type='package',
            capacity='member'
        )
    return


def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    dc.ensure_publisher('gp-survey')
    dc.ensure_group('surveys')

    def year_as_key(x):
        return x['title'][-4:]

    datasets = json.load(open(os.path.join(DATA_DIR, "metadata.json"), "r"))
    datasets = sorted(datasets, key=year_as_key)
    for dataset in datasets:
        load_statistic(dataset, DATA_DIR)
        groups(dataset)
