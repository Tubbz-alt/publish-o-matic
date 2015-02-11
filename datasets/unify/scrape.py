"""
Build metadata from unify.datasets.csv and also scrape the
resources from the linked pages.
"""
import json
import os
import sys
import urllib

import ffs
from lxml.html import fromstring, tostring
import requests
import slugify


DATA_DIR = None

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    return 0
