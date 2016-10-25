"""
Scrape the MHMDS
"""
import json
import sys

import ffs
import html2text
from lxml.html import fromstring, tostring
import re
import requests

HERE = ffs.Path.here()
DATA_DIR = None
INDEX_URL = 'http://www.hscic.gov.uk/mhldsreports'

def _hscic_resources_from_tree(tree):
    resource_dicts = []
    resources = tree.cssselect('.resourcelink a')
    for resource in resources:
        url = resource.get('href')
        if not url:
            print resource
        format = url.split('.')[-1]
        description = resource.text_content().strip()
        resource_dicts.append(dict(url=url, description=description, format=format))
    return resource_dicts


def mhds_dataset(url):
    """
    From a base url, return a dict containing this dataset's metadata and resources.
    """
    print url
    dataset = {}
    dataset_tree = _astree(url)
    dataset['source'] = url
    title = dataset_tree.cssselect('#headingtext')[0].text_content().strip()
    dataset['title'] = title
    publication_date = dataset_tree.cssselect('.pubdate')[0].text_content().strip().replace('Publication date: ', '')
    dataset['publication_date'] = publication_date
    summary = html2text.html2text(tostring(dataset_tree.cssselect('.summary')[0]))
    dataset['summary'] = summary
    dataset['resources'] = _hscic_resources_from_tree(dataset_tree)
    return dataset

def _astree(url):
    """
    Helper that returns a URL as a lxml tree
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        print resp
        raise Exception('FTWError - File Not Found')
    content = resp.text
    dom = fromstring(content)
    dom.make_links_absolute(url)
    return dom


def find_datasets():
    index = _astree(INDEX_URL)
    datasets = index.cssselect('#bodytext a')
    return [a.get('href') for a in datasets]

def retrieve_datasets(datasets):
    for dataset in datasets:
        dataset = mhds_dataset(dataset)
        dataset_dir = DATA_DIR/dataset['title']
        dataset_dir.mkdir()
        metadata_file = dataset_dir/'dataset.metadata.json'
        print metadata_file
        if metadata_file:
            metadata_file.truncate()
        metadata_file << json.dumps(dataset, indent=2)

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    datasets = find_datasets()
    retrieve_datasets(datasets)
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))

