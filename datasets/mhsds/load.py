import ffs
import dc
import ffs


def load_data(datasets):
    for metadata in datasets:
        tags = metadata['tags']
        tags.append('Mental Health')
        resources = [
            dict(
                description=r['description'],
                name=r['url'].split('/')[-1],
                format=r['format'],
                url=r['url']
                #upload=open(str(directory/r['url'].split('/')[-1]), 'r')
            )
            for r in metadata['resources']
        ]
        dc.Dataset.create_or_update(
            name=metadata["name"],
            title=metadata['title'],
            state='active',
            license_id='uk-ogl',
            notes=metadata['notes'],
            origin=metadata['source'],
            tags=dc.tags(*tags),
            resources=resources,
            owner_org='hscic',
            coverage_start_date=metadata['coverage_start_date'],
            coverage_end_date=metadata['coverage_end_date'],
            extras=[
                dict(
                    key='publication date',
                    value=metadata['publication_date']
                ),
                # note when we move to CKAN 2.5 this should be changed to a kwarg
                dict(key='frequency', value=metadata['frequency']),
            ]
        )

def group_data(datasets):
    for metadata in datasets:
        dataset = dc.ckan.action.package_show(id=metadata["name"])

        if [g for g in dataset['groups'] if g['name'].lower() == 'mhsds']:
            print 'Already in group', g

        else:
            dc.ckan.action.member_create(
                id='mhsds',
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )


def main(workspace):
    dataset_file = ffs.Path(workspace) / 'data/mhsds/dataset.metadata.json'

    datasets = dataset_file.json_load()
    load_data(datasets)
    group_data(datasets)
    dc.ensure_publisher('hscic')
    dc.ensure_group("mhsds")
    return 0
