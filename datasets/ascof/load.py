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

def load_ascof():
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
        slug = slugify.slugify(metadata['title']).lower()
        print 'Creating', metadata['title'], slug
        dc.Dataset.create_or_update(
            name=slug,
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
    return

def group_ascof():
    for _, _, metadata in datasets():
        dataset_name = slugify.slugify(metadata['title']).lower()
        dataset = dc.ckan.action.package_show(id=dataset_name)

        if [g for g in dataset['groups'] if g['name'].lower() == 'ascof']:
            print 'Already in group', g

        else:
            dc.ckan.action.member_create(
                id='ascof',
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    dc.ensure_publisher('hscic')
    dc.ensure_group('ascof')
    load_ascof()
    group_ascof()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
