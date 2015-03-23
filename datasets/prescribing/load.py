"""
Load the Statistic datasets into a CKAN instance
"""
import hashlib
import json
import os
import sys

import dc
import ffs



def load_dataset(dataset, directory):
    print 'Creating', dataset['title'], dataset['name']
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
            license_id='uk-ogl',
            notes=dataset['notes'],
            origin=dataset['origin'],
            tags=dc.tags(*dataset['tags']),
            resources=dataset["resources"],
            owner_org='hscic',
            extras=extras,
            coverage_start_date=dataset.get('coverage_start_date', ''),
            coverage_end_date=dataset.get('coverage_end_date', ''),
        )
    except Exception, e:
        print "ERROR: Problem updating/creating dataset - {}".format(dataset['name'])
        import traceback
        traceback.print_exc()
        print ".{}.{}.".format(dataset['coverage_start_date'], dataset['coverage_end_date'])
        sys.exit(0)



def main(workspace):
    DATA_DIR = ffs.Path(workspace)

    dc.ensure_publisher('hscic')

    datasets = json.load(open(os.path.join(DATA_DIR, "metadata.json"), "r"))
    for dataset in datasets:
        load_dataset(dataset, DATA_DIR)
