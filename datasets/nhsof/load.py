"""
Load the QOF datasets into a CKAN instance
"""
import os
import dc
import ffs
import json
import slugify

from publish.lib.metadata import get_resource_file

def load_ccgois(datasets):
    counter = 0

    # There are only 35 datasets from the scrape, why are we skipping 43.
    for metadata in datasets: #[43:]:
        counter += 1
        resources = []
        for r in metadata['sources']:
            upload = dc.fh_for_url(r['url'])
            resources.append({
                'description': r['description'],
                'name': r['url'].split('/')[-1],
                'format': r['filetype'],
                'upload': upload,
            })

        print "Resources ready for upload"
        metadata['title'] = 'NHSOF - ' + metadata['title']
        print u'Creating dataset'
        try:
            dc.Dataset.create_or_update(
                name=slugify.slugify(metadata['title']).lower()[:99],
                title=metadata['title'],
                state='active',
                license_id='uk-ogl',
                notes=metadata['description'],
                url='https://indicators.ic.nhs.uk/webview/',
                tags=dc.tags(*metadata['keyword(s)']),
                resources=resources,
                #frequency=['Other', ],
                owner_org='hscic',
                extras=[
                    dict(key='frequency', value='Other'),
                    dict(key='coverage_start_date', value=metadata['coverage_start_date']),
                    dict(key='coverage_end_date', value=metadata['coverage_end_date']),
                    dict(key='domain', value=metadata['domain']),
                    dict(key='origin', value='HSCIC'),
                    dict(key='next_version_due', value=metadata['next version due']),
                    dict(key='HSCIC_unique_id', value=metadata['unique identifier']),
                    dict(key='homepage', value=metadata['homepage']),
                    dict(key='status', value=metadata['status']),
                    dict(key='language', value=metadata['language']),
                    dict(key='release_date', value=metadata['current version uploaded'])

                ]
            )
        except:
            print u"Failed to create {}".format(slugify.slugify(metadata['title']).lower()[:99])
    return counter

def group_ccgois(datasets):
    for metadata in datasets:
        #metadata['title'] = 'NHSOF - ' + metadata['title']
        dataset_name = slugify.slugify(metadata['title']).lower()[:99]
        print dataset_name

        try:
            dataset = dc.ckan.action.package_show(id=dataset_name)
        except:
            print u"Could not find dataset: {}".format(dataset_name)
            continue

        if [g for g in dataset.get('groups', []) if g['name'] == 'nhsof']:
            print 'Already in group', g['name']
        else:
            dc.ckan.action.member_create(
                id='nhsof',
                object=dataset_name,
                object_type='package',
                capacity='member'
            )
    return



DATA_DIR = None

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    datasets = json.load(get_resource_file(DATA_DIR / 'nhsof_metadata_indicators.json'))
    print "Ensuring publisher"
    dc.ensure_publisher('hscic')
    print "Ensuring group"
    dc.ensure_group('nhsof')
    wrote = load_ccgois(datasets)
    if wrote:
        group_ccgois(datasets)
    else:
        print "Created/processed no datasets ..."

if __name__ == '__main__':
    main(ffs.Path.here())
