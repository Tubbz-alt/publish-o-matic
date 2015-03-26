"""
Scrape Patient Practice datasets
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

DATA_DIR = None

def find_pp_datasets():
    """
    Iterate through the scraped HSCIC Metadata and then spit out our
    datasets.
    """
    datasets = []
    find = 'Numbers of Patients Registered at a GP Practice'
    new_datasets = json.load(open(get_resource_path("datasets.json")))
    for dataset in new_datasets:
        if dataset['title'].startswith(find):
            print "Found :", dataset['title']
            datasets.append(dataset)
    return datasets

def retrieve_pp_datasets(datasets):
    for dataset in datasets:
        print dataset['title']
        dataset_dir = DATA_DIR/dataset['title']
        dataset_dir.mkdir()
        metadata_file = dataset_dir/'dataset.metadata.json'
        if metadata_file:
            metadata_file.truncate()
        metadata_file << json.dumps(dataset, indent=2)

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    datasets = find_pp_datasets()
    retrieve_pp_datasets(datasets)

