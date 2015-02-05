"""
Load the ASCODF datasets into a CKAN instance
"""
import sys

import dc
import ffs
import slugify

HERE = ffs.Path.here()
DATA_DIR = HERE / 'data'

def datasets():
    metadata = DATA_DIR/'dataset.metadata.json'
    yield DATA_DIR, metadata, metadata.json_load()

def load_phe():
    for directory, metadata_file, metadata in datasets():
        resources = [
            dict(
                description=r['description'],
                name=r['url'].split('/')[-1],
                format=r['filetype'],
                upload=open(str(directory/r['url'].split('/')[-1]), 'r')
            )
            for r in metadata['resources']
        ]
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
            extras=[
                dict(key='coverage_beginning_date', value=metadata['coverage_beginning_date']),
                dict(key='coverage_ending_date', value=metadata['coverage_ending_date']),
                dict(key='frequency', value=metadata['frequency']),
                dict(key='publication_date', value=metadata['publication_date'])
            ]
        )
    return

def group_phe():
    for _, _, metadata in datasets():
        dataset_name = slugify.slugify(metadata['title']).lower()
        dataset = dc.ckan.action.package_show(id=dataset_name)
        
        if [g for g in dataset['groups'] if g['name'].lower() == 'phe']:
            print 'Already in group', group

        else:
            dc.ckan.action.member_create(
                id='phe', 
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )
    return

def main():
    dc.ensure_publisher('phe')
    dc.ensure_group('PHOF')
    load_phe()
    group_phe()
    return 0

if __name__ == '__main__':
    sys.exit(main())
