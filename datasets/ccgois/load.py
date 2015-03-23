"""
Load the CCGOIS datasets into a CKAN instance
"""
import dc
import json
import slugify
import ffs

def make_name_from_title(title):
    # For some reason, we're finding duplicate names
    name = slugify.slugify(title).lower()[:99]
    if not name.startswith('ccgois-'):
        name = u"ccgois-{}".format(name)
    return name


def load_ccgois(datasets):
    for metadata in datasets:
        resources = [
            dict(
                description=r['description'],
                name=r['name'],
                format=r['filetype'],
                url=r['url']
            )
            for r in metadata['resources']
        ]

        print [r['name'] for r in metadata['resources']]

        metadata['title'] = u'CCGOIS - {}'.format(metadata['title'])
        metadata['name'] = make_name_from_title(metadata['title'])
        print u'Creating {}'.format(metadata['name'])
        dc.Dataset.create_or_update(
            name=metadata['name'],
            title=metadata['title'],
            state='active',
            license_id='uk-ogl',
            notes=metadata['description'],
            origin='https://indicators.ic.nhs.uk/webview/',
            tags=dc.tags(*metadata['keyword(s)']),
            resources=resources,
            #frequency=[metadata['frequency'], ],
            owner_org='hscic',
            extras=[
                dict(key='frequency', value=metadata.get('frequency', '')),
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
        dataset_name = make_name_from_title(metadata['title'])

        try:
            dataset = dc.ckan.action.package_show(id=dataset_name)
        except:
            print "Failed to find dataset: {}".format(dataset_name)
            print "Can't add to group"
            continue

        if [g for g in dataset.get('groups', []) if g['name'] == 'ccgois']:
            print 'Already in group', g['name']
        else:
            dc.ckan.action.member_create(
                id='ccgois',
                object=dataset_name,
                object_type='package',
                capacity='member'
            )
    return

def main(workspace):
    DATA_DIR = ffs.Path(workspace)
    datasets = json.load(open(DATA_DIR / 'ccgois_indicators.json'))
    dc.ensure_publisher('hscic')
    dc.ensure_group('ccgois')
    load_ccgois(datasets)
    group_ccgois(datasets)
