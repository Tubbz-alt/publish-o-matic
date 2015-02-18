"""
Scrape QOF datas
"""
import json
import sys
import urllib

import ffs
import html2text
from lxml.html import fromstring, tostring
import re
import requests

from publish.lib.metadata import get_resource_path
from publish.lib.helpers import filename_for_resource, download_file
from publish.lib.upload import Uploader


DATA_DIR = None

HSCIC_DATASETS = get_resource_path('data/datasets.json')

QOF_ROOT = 'http://www.hscic.gov.uk/qof'


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
        name = url.split('/')[-1]
        description = resource.text_content().strip()
        resource_dicts.append(dict(url=url, description=description, format=filetype.upper(), name=name))
    return resource_dicts

def qof_dataset(url):
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

    alternative_granularities = [a.get('href') for a in dataset_tree.cssselect('.interestlinks a')]
    for gran in alternative_granularities:
        print 'Granularity', gran
        dataset['resources'] += _hscic_resources_from_tree(_astree(gran))

    return dataset

def find_qof_datasets():
    qof_tree = _astree(QOF_ROOT)
    all_datasets = qof_tree.cssselect('h3 a')
    interesting = sorted([a.get('href') for a in all_datasets
                   if re.match(r'^The Quality and Outcomes Framework [\d]{4}-[\d]{2}$', a.text_content())])

    datasets = []
    for dataset in interesting:
        datasets.append(qof_dataset(dataset))
    # for dataset in HSCIC_DATASETS.json_load():
    #     if re.match(r'^Quality and Outcomes Framework - [\d]{4}-[\d]{2}$', dataset['title']):
    #         datasets.append(dataset)
    return datasets

def retrieve_qof_datasets(datasets):
    u = Uploader("qof")

    for dataset in datasets:
        print dataset['title']
        dataset_dir = DATA_DIR/dataset['title']
        dataset_dir.mkdir()
        with dataset_dir:
            for resource in dataset['resources']:
                filename = filename_for_resource(resource)
                path = dataset_dir / filename

                download_file(resource['url'], path)
                print "Uploading to S3"
                url = u.upload(path)
                resource['url'] = url



        metadata_file = dataset_dir/'dataset.metadata.json'
        if metadata_file:
            metadata_file.truncate()
        metadata_file << json.dumps(dataset, indent=2)

    u.close()


def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / "data"
    datasets = find_qof_datasets()
    retrieve_qof_datasets(datasets)
    return 0

