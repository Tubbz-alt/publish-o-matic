"""
Load the QOF datasets into a CKAN instance
"""
import dc
import json
import slugify

def load_ccgois(datasets):
    for metadata in datasets[16:]:
        resources = [
            dict(
                description=r['description'],
                name=r['url'].split('/')[-1],
                format=r['filetype'],
                upload=dc.fh_for_url(r['url'])
            )
            for r in metadata['sources']
        ]
        metadata['title'] = 'CCGOIS - ' + metadata['title']
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
            frequency=[metadata['frequency'], ],
            owner_org='hscic',
            extras=[
                dict(key='coverage_start_date', value=metadata['coverage_start_date']),
                dict(key='coverage_end_date', value=metadata['coverage_end_date']),
                dict(key='domain', value=metadata['domain']),
                dict(key='origin', value='HSCIC'),
                dict(key='next_version_due', value=metadata['next version due']),
                dict(key='nhs_OF_indicators', value=metadata['nhs_of_indicators']),
                dict(key='HSCIC_unique_id', value=metadata['unique identifier']),
                dict(key='homepage', value=metadata['homepage']),
                dict(key='status', value=metadata['status']),
                dict(key='language', value=metadata['language']),
                dict(key='assurance_level', value=metadata['assurance_level']),
                dict(key='release_date', value=metadata['current version uploaded'])

            ]
        )
    return

def group_ccgois(datasets):
    for metadata in datasets:
        metadata['title'] = 'CCGOIS - ' + metadata['title']
        dataset_name = slugify.slugify(metadata['title']).lower()[:99]
        dataset = dc.ckan.action.package_show(id=dataset_name)

        if [g for g in dataset.get('groups', []) if g['name'] == 'ccgois']:
            print 'Already in group', g
        else:
            dc.ckan.action.member_create(
                id='ccgois',
                object=dataset_name,
                object_type='package',
                capacity='member'
            )
    return

def main(workspace):
    datasets = json.load(open('ccgois_indicators.json'))
    dc.ensure_publisher('hscic')
    dc.ensure_group('ccgois')
    #load_ccgois(datasets)
    group_ccgois(datasets)

if __name__ == '__main__':
    main(None)
