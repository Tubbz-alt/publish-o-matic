"""
Publish HSCIC Indicators to CKAN !
"""
import logging
import sys
import ffs

import dc


logging.basicConfig(filename='publish.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)


DATA_DIR = ffs.Path.here()/'../data'


def publish_indicators(start_from=0):
    indicatorfile = DATA_DIR/'indicators.json'
    logging.info('Loading {}'.format(indicatorfile))
    indicators = indicatorfile.json_load()
    logging.info('Processing {} indicators'.format(len(indicators)))
    logging.info('Starting from record {}'.format(start_from))
    for indicator in indicators[start_from:]:
        logging.info('Processing {}'.format(indicator['title']))
        logging.info('ID: {}'.format(indicator['unique identifier'].lower()))
        try:
            resources = [
                dict(
                    description=s['description'],
                    name=s['url'].split('/')[-1],
                    format=s['filetype'],
                    upload=dc.fh_for_url(s['url'])
                )
                for s in indicator['sources']
            ]
            dc.Dataset.create_or_update(
                name=indicator['unique identifier'].lower(),
                title=indicator['title'],
                state='active',
                licence_id='ogl',
                notes=indicator['definition'],
                url='https://indicators.ic.nhs.uk/webview/',
                tags=dc.tags(*indicator['keyword(s)']),
                resources=resources,
                owner_org='hscic'
            )
        except Exception as ex:
            logging.error(ex)
    return

def publish_datasets(start_from=0):
    datasetfile = DATA_DIR/'datasets.json'
    logging.info('Loading {}'.format(datasetfile))
    datasets = datasetfile.json_load()
    logging.info('Processing {} indicators'.format(len(datasets)))
    logging.info('Starting from record {}'.format(start_from))
    for dataset in datasets[start_from:]:
        logging.info('Processing {}'.format(dataset['title']))
        logging.info('ID: {}'.format(dataset['id']))
        try:
            resources = [
                dict(
                    description=s['description'],
                    name=s['url'].split('/')[-1],
                    format=s['filetype'],
                    upload=dc.fh_for_url(s['url'])
                )
                for s in dataset['sources']
            ]
            notes = dataset['summary']
            if 'key_facts' in dataset:
                notes += '\n\nKEY FACTS:\n==========\n\n' + dataset['key_facts']
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
            logging.error(ex)
    return

def main():
    dc.ensure_publisher('hscic')
    publish_indicators(266)
    publish_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main())
