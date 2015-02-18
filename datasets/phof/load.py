"""
No longer required/used

Load the PHOF datasets into a CKAN instance
"""
import json
import sys

import dc
import ffs
import slugify

DATA_DIR = None


def load_phe():

    metadata = json.load(open(DATA_DIR/'dataset.metadata.json'))

    resources = [
        dict(
            description=r['description'],
            name=r['name'],
            format=r['format'],
            url='url'
        )
        for r in metadata['resources']
    ]

    extras = [
            dict(key='frequency', value=metadata['frequency']),
        ]
    if 'publication_date' in metadata:
        extras.append(dict(key='publication_date', value=metadata['publication_date']))
    extras.append(dict(key='coverage_start_date', value=metadata.get('coverage_start_date','')))
    extras.append(dict(key='coverage_end_date', value=metadata.get('coverage_end_date')))

    print extras

    print 'Creating', metadata['title']
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
        #extras=extras
    )
    return

def group_phe():
    for _, _, metadata in datasets():
        dataset_name = slugify.slugify(metadata['title']).lower()
        dataset = dc.ckan.action.package_show(id=dataset_name)

        if [g for g in dataset['groups'] if g['name'].lower() == 'phe']:
            print 'Already in group', g

        else:
            dc.ckan.action.member_create(
                id='phe',
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    dc.ensure_publisher('phe')
    dc.ensure_group('phof')
    load_phe()
    #group_phe()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
