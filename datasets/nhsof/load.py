"""
Load the QOF datasets into a CKAN instance
"""
import dc
import json
import slugify

def load_ccgois(datasets):
    counter = 0
    for metadata in datasets[43:]:
        print counter
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
        metadata['title'] = 'NHSOF - ' + metadata['title']
        print 'Creating', metadata['title']
        dc.Dataset.create_or_update(
            name=slugify.slugify(metadata['title']).lower()[:99],
            title=metadata['title'],
            state='active',
            license_id='uk-ogl',
            notes=metadata['description'],
            url='https://indicators.ic.nhs.uk/webview/',
            tags=dc.tags(*metadata['keyword(s)']),
            resources=resources,
            frequency=['Other', ],
            owner_org='hscic',
            extras=[
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
    return

def group_ccgois(datasets):
    for metadata in datasets:
        metadata['title'] = 'NHSOF - ' + metadata['title']
        dataset_name = slugify.slugify(metadata['title']).lower()[:99]
        print dataset_name
        dataset = dc.ckan.action.package_show(id=dataset_name)

        if [g for g in dataset.get('groups', []) if g['name'] == 'nhsof']:
            print 'Already in group'
        else:
            dc.ckan.action.member_create(
                id='nhsof',
                object=dataset_name,
                object_type='package',
                capacity='member'
            )
    return


if __name__ == '__main__':
    datasets = json.load(open('nhsof_metadata_indicators.json'))
    dc.ensure_publisher('hscic')
    dc.ensure_group('NHSOF', 'hscic')
    #load_ccgois(datasets)
    group_ccgois(datasets)
