"""
Publish HSCIC Indicators to CKAN !
"""
import logging
import sys
import ffs
import slugify

import dc
from publish.lib.metadata import get_resource_path

from publish.lib.helpers import download_file, to_markdown, filename_for_resource
from publish.lib.upload import Uploader
from datasets.hscic.curate import Curator

logging.basicConfig(filename='publish.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)

DATA_DIR = None

# TODO: Change this to just strip punctuation and check length
def clean_tag(t):
    def valid_only(tags):
        return [tag for tag in tags if len(tag) > 2]

    t = t.replace('(', "").replace(")", "").replace(':', "")
    t = t.replace('A+E', "A and E")
    t = t.replace('ST&amp', "")
    t = t.replace('A&amp', "A and")
    if ';' in t:
        return valid_only([s.strip() for s in t.split(';')])
    elif '/' in t:
        return valid_only([s.strip() for s in t.split('/')])
    return valid_only([t.replace('&', '-and-')])


def publish_indicators(start_from=0):
    global DATA_DIR
    u = Uploader("hscic-indicators")

    indicatorfile = ffs.Path(get_resource_path('indicators.json'))
    logging.info('Loading {}'.format(indicatorfile))
    indicators = indicatorfile.json_load()
    logging.info('Processing {} indicators'.format(len(indicators)))
    logging.info('Starting from record {}'.format(start_from))
    for indicator in indicators[start_from:]:
        try:
            resources = []
            for s in indicator['sources']:
                resource = {
                    "description": s['description'],
                    "name": s['url'].split('/')[-1],
                    "format": s['filetype'].upper(),
                    "url": s["url"]
                }

                """
                filename = filename_for_resource(resource)
                path = DATA_DIR / filename
                download_file(resource['url'], path)
                print "Uploading to S3"
                url = u.upload(path)
                resource['url'] = url
                """
                resources.append(resource)

            if not 'indicators' in indicator['keyword(s)']:
                indicator['keyword(s)'].append('indicators')

            title = indicator['title']

            c = Curator(indicator)
            groups = c.get_groups()
            if not groups:
                print "Not in a group"
                continue

            prefix = c.get_title_prefix()
            if prefix:
                title = u"{} - {}".format(prefix, title)

            tags = []
            if 'keyword(s)' in dataset:
                dataset['keyword(s)'] = sum([clean_tag(k) for k in indicator.get('keyword(s)',[]) if len(k) > 2], [])
                tags = dc.tags(*dataset['keywords'])


            print '+ Create/Update dataset {}'.format(indicator['title'])
            dc.Dataset.create_or_update(
                name=slugify.slugify(title).lower()[:99],
                title=title,
                state='active',
                licence_id='ogl',
                notes=to_markdown(indicator['definition'].encode('utf8')),
                url='https://indicators.ic.nhs.uk/webview/',
                tags=dc.tags(tags),
                resources=resources,
                owner_org='hscic'
            )

            if groups:
                try:
                    dataset = dc.ckan.action.package_show(id=slugify.slugify(title)[:99].lower())
                except:
                    continue

                for group in groups:
                    group = group.lower()

                    if [g for g in dataset.get('groups', []) if g['name'] == group]:
                        print 'Already in group', g['name']
                    else:
                        dc.ckan.action.member_create(
                            id=group,
                            object=dataset_name,
                            object_type='package',
                            capacity='member'
                        )

        except Exception as ex:
            import traceback
            traceback.print_exc()
            import sys; sys.exit(1)

    u.close()
    return

def publish_datasets(start_from=0):
    global DATA_DIR

    u = Uploader("hscic-datasets")

    datasetfile = ffs.Path(get_resource_path('datasets.json'))
    logging.info('Loading {}'.format(datasetfile))
    datasets = datasetfile.json_load()
    logging.info('Processing {} indicators'.format(len(datasets)))
    logging.info('Starting from record {}'.format(start_from))

    import random
    total = len(datasets) - start_from
    current = 1

    for dataset in datasets[start_from:]:
        print "STATUS: {}/{}".format(current, total)
        current += 1

        #print u'Processing {}'.format(dataset['title'])
        #print '  ID: {}'.format(dataset['id'])
        try:
            resources = []
            for s in dataset['sources']:
                resource = {
                        "description": s['description'],
                        "name": s['url'].split('/')[-1],
                        "format": s['filetype'],
                        "url": s["url"]
                }
                """
                filename = filename_for_resource(resource)
                path = DATA_DIR / filename
                download_file(resource['url'], path)
                resource['url'] = u.upload(path)
                """
                resources.append(resource)

            if not resources:
                print "Dataset {} does not have any resources".format(dataset['id'])
                continue

            title = dataset['title']

            c = Curator(dataset)
            groups = c.get_groups()
            if not groups:
                print "Not in a group"
                continue

            prefix = c.get_title_prefix()
            if prefix:
                title = u"{} - {}".format(prefix, title)
            name = slugify.slugify(title).lower()[0:99]

            # Call cleantags on each work and expect back a list, which is then flattened

            tags = []
            if 'keywords' in dataset:
                dataset['keywords'] = sum([clean_tag(k) for k in dataset.get('keywords',[]) if len(k) > 2], [])
                tags = dc.tags(*dataset['keywords'])

            notes = dataset['summary']
            if 'key_facts' in dataset:
                notes += '\n\n<h2>KEY FACTS:</h2>\n' + ''.join(dataset['key_facts'])
            notes = to_markdown(notes)


            name = 'hscic_dataset_{}'.format(dataset['id'])

            dc.Dataset.create_or_update(
                name=name,
                title=title,
                state='active',
                licence_id='ogl',
                notes=notes,
                url=dataset['source'],
                tags=tags,
                resources=resources,
                owner_org='hscic'
            )

            if groups:
                try:
                    dataset = dc.ckan.action.package_show(id=name)
                except:
                    continue

                for group in groups:
                    group = group.lower()

                    if [g for g in dataset.get('groups', []) if g['name'] == group]:
                        print 'Already in group', g['name']
                    else:
                        dc.ensure_group(group)
                        dc.ckan.action.member_create(
                            id=group,
                            object=dataset['id'],
                            object_type='package',
                            capacity='member'
                        )
        except Exception as ex:
            import traceback
            traceback.print_exc()

    u.close()
    return

def load(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / "data"
    DATA_DIR.mkdir()

    dc.ensure_publisher('hscic')
    publish_indicators(0)
    publish_datasets(0)
    return 0
