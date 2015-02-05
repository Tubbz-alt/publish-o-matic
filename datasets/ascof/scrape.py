"""
Scrape ASCOF datasets
"""
import json
import sys
import urllib

import ffs
import html2text
from lxml.html import fromstring, tostring
import re
import requests

HERE = ffs.Path.here()
DATA_DIR = None
METADATA_DIR = HERE / '../../metadata/data'

HSCIC_DATASETS = METADATA_DIR/'datasets.json'

ASCOF_DATASETS = [
    'http://www.hscic.gov.uk/article/2021/Website-Search?productid=16655&q=Measures+from+the+Adult+Social+Care+Outcomes+Framework%2c+England+Final&sort=Relevance&size=100&page=1&area=both#top',
    'http://www.hscic.gov.uk/article/2021/Website-Search?productid=13856&q=Measures+from+the+Adult+Social+Care+Outcomes+Framework%2c+England+Final&sort=Relevance&size=100&page=1&area=both#top',
    'http://www.hscic.gov.uk/article/2021/Website-Search?productid=11117&q=Measures+from+the+Adult+Social+Care+Outcomes+Framework%2c+England+Final&sort=Relevance&size=100&page=1&area=both#top'
]

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

def _hscic_resources_from_tree(tree):
    resource_dicts = []
    resources = tree.cssselect('.resourcelink a')
    for resource in resources:
        url = resource.get('href')
        if not url:
            print resource
        filetype = url.split('.')[-1]
        description = resource.text_content().strip()
        resource_dicts.append(dict(url=url, description=description, filetype=filetype))
    return resource_dicts


def ascof_dataset(url):
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

def find_ascof_datasets():
    """
    Iterate through the scraped HSCIC Metadata and then spit out our
    datasets.
    """
    datasets = []
    for dataset in ASCOF_DATASETS:
        datasets.append(ascof_dataset(dataset))
    return datasets

def retrieve_ascof_datasets(datasets):
    for dataset in datasets:
        print dataset['title']
        dataset_dir = DATA_DIR/dataset['title']
        dataset_dir.mkdir()
        with dataset_dir:
            for resource in dataset['resources']:
                print resource['url']
                urllib.urlretrieve(resource['url'], resource['url'].split('/')[-1])
        metadata_file = dataset_dir/'dataset.metadata.json'
        if metadata_file:
            metadata_file.truncate()
        metadata_file << json.dumps(dataset, indent=2)

def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'

    datasets = find_ascof_datasets()
    retrieve_ascof_datasets(datasets)
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
