"""
Publish HSCIC Indicators to CKAN !
"""
import logging
import sys
import ffs

import dc
from publish.lib.metadata import get_resource_path
from publish.lib.helpers import download_file, to_markdown, filename_for_resource
from publish.lib.upload import Uploader

logging.basicConfig(filename='publish.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)

DATA_DIR = None

def publish_indicators(start_from=0):
    global DATA_DIR
    u = Uploader("hscic-indicators")

    indicatorfile = ffs.Path(get_resource_path('indicators.json'))
    logging.info('Loading {}'.format(indicatorfile))
    indicators = indicatorfile.json_load()
    logging.info('Processing {} indicators'.format(len(indicators)))
    logging.info('Starting from record {}'.format(start_from))
    for indicator in indicators[start_from:]:
        print 'Processing {}'.format(indicator['title'])
        print ' ID: {}'.format(indicator['unique identifier'].lower())
        try:
            resources = []
            print " {} has {} sources".format(indicator['title'], len(indicator['sources']))
            for s in indicator['sources']:
                resource = {
                    "description": s['description'],
                    "name": s['url'].split('/')[-1],
                    "format": s['filetype'].upper(),
                    "url": s["url"]
                }

                filename = filename_for_resource(resource)
                path = DATA_DIR / filename
                download_file(resource['url'], path)
                print "Uploading to S3"
                url = u.upload(path)
                resource['url'] = url
                resources.append(resource)

            if not 'indicators' in indicator['keyword(s)']:
                indicator['keyword(s)'].append('indicators')

            print '+ Create/Update dataset {}'.format(indicator['title'])
            dc.Dataset.create_or_update(
                name=indicator['unique identifier'].lower(),
                title=indicator['title'],
                state='active',
                licence_id='ogl',
                notes=to_markdown(indicator['definition']),
                url='https://indicators.ic.nhs.uk/webview/',
                tags=dc.tags(*indicator['keyword(s)']),
                resources=resources,
                owner_org='hscic'
            )
        except Exception as ex:
            print ex
            import sys; sys.exit(0)

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
    for dataset in datasets[start_from:]:
        print 'Processing {}'.format(dataset['title'])
        print '  ID: {}'.format(dataset['id'])
        try:
            resources = []
            for s in dataset['sources']:
                print s['url']
                resource = {
                        "description": s['description'],
                        "name": s['url'].split('/')[-1],
                        "format": s['filetype'],
                        "url": s["url"]
                }

                filename = filename_for_resource(resource)
                path = DATA_DIR / filename
                download_file(resource['url'], path)
                print "Uploading to S3"
                resource['url'] = u.upload(path)

                resources.append(resource)

            if not 'indicators' in dataset['keywords']:
                dataset['keywords'].append('indicators')

            notes = dataset['summary']
            if 'key_facts' in dataset:
                notes += '\n\n<h2>KEY FACTS:</h2>\n' + ''.join(dataset['key_facts'])
            notes = to_markdown(notes.encode('utf8'))
            name = 'hscic_dataset_{}'.format(dataset['id'])
            dc.Dataset.create_or_update(
                name=name,
                title=dataset['title'],
                state='active',
                licence_id='ogl',
                notes=notes,
                url=dataset['source'],
                tags=dc.tags(*dataset['keywords']),
                resources=resources,
                owner_org='hscic'
            )
        except Exception as ex:
            import traceback
            traceback.print_exc()
            import sys; sys.exit(0)

    u.close()
    return

def load(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / "data"
    DATA_DIR.mkdir()

    dc.ensure_publisher('hscic')
    #publish_indicators( 0) #266)
    publish_datasets()
    return 0
