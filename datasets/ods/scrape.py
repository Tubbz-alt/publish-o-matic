"""
Scrape ODS data from the HSCIC
"""
import hashlib
import json
import os
import re
import sys
import urllib

import ffs
from lxml.html import fromstring, tostring
import requests
import slugify

from datasets.ods.info import DATASETS
from publish.lib.helpers import download_file, to_markdown, remove_tables_from_dom

PREFIX = "ODS"

title_matcher = re.compile('^(.*)\((.*), .*\)$')

def _astree(url):
    """
    Helper that returns a URL as a lxml tree
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('FTWError - File Not Found')
    content = resp.text
    dom = fromstring(content)
    dom.make_links_absolute(url)
    return dom


def process_link(link):
    """
    Get text and link from an anchor
    """
    return link.text_content(), link.get('href')


def build_resource(date, text, link):
    ext = link[-3:].upper()

    description = text

    m = title_matcher.match(description)
    if m:
        description = m.groups(0)[0]
        if  m.groups(0)[1] != ext:
            ext = m.groups(0)[1]

    return {
        'url': link,
        "name": link.split('/')[-1],
        "format": ext,
        "description": description.strip(),
        "url_type": "",
    }


def build_desc_from_dom(desc_html):
    desc_dom = fromstring(desc_html)
    remove_tables_from_dom(desc_dom)
    return to_markdown(tostring(desc_dom))

def download_and_hash_file(dataset_name, url):
    folder = DATA_DIR / dataset_name
    folder.mkdir()

    hash_of_url = hashlib.sha224(url).hexdigest()
    print download_file(url, os.path.join(folder, hash_of_url))


###############################################################################
# Multi-datasets on a single page.... ugh
###############################################################################
def build_dataset(header, desc, table_rows):
    desc_html = to_markdown("\n".join(desc))

    metadata = {
        "name": "{}-{}".format(PREFIX.lower(), slugify.slugify(header).lower()),
        "title": u"{} - {}".format(PREFIX, header),
        "notes": desc_html,
        "coverage_start_date": "",
        "coverage_end_date": "",
        "frequency": "",
        "tags": ["ODS", "Organisation Data Service"],
        "resources": []
    }

    date_string = ""

    for row in table_rows:

        for cell in row:
            link = cell.cssselect('a')
            if not len(link):
                date_string = cell.text_content().strip()
                continue

            text = link[0].text_content().strip()
            href = link[0].get('href')

        metadata["resources"].append(build_resource(date_string, text, href))

    return metadata

def process_multi(dataset):
    """
    Multiple datasets on one page, so we'll track them with:
        a H3 for header
        followed by p tags
        until we find the table
    """
    dom = _astree(dataset['url']).cssselect("#parent-fieldname-text")[0]

    datasets = []

    h3 = None
    desc = []
    table_rows = None

    for element in dom:
        if element.tag.upper() == "H3":
            if h3 and table_rows:
                datasets.append(build_dataset(h3, desc, table_rows))
            h3 = element.text_content().strip()
            desc = []
            table_rows = None
            continue
        elif element.tag.upper() in ["P", "DIV"] :
            desc.append(element.text_content().encode("utf8"))
        elif element.tag.upper() == "UL":
            desc.append(tostring(element))
        elif element.tag.upper() == "TABLE":
            table_rows = element.cssselect("tr")[1:]

    if h3 and table_rows:
        datasets.append(build_dataset(h3, desc, table_rows))

    return datasets

###############################################################################


def process_dataset(dataset):
    print "Processing '{}'".format(dataset['url'])

    if dataset.get("multi", False):
        return process_multi(dataset)

    dom = _astree(dataset['url'])
    title = dom.xpath(dataset['title'])[0].text_content().strip()

    desc_html = "\n".join(tostring(dom.xpath(x)[0]) for x in dataset['description'])
    description = build_desc_from_dom(desc_html)

    metadata = {
        "name": "{}-{}".format(PREFIX.lower(), slugify.slugify(title).lower()),
        "title": "{} - {}".format(PREFIX, title),
        "notes": description,
        "coverage_start_date": "",
        "coverage_end_date": "",
        "frequency": "",
        'tags': ["ODS", "Organisation Data Service"]
    }

    resources = []


    loose_links = dom.cssselect('p a')
    if len(loose_links) > 0:
        # ""
        for loose in loose_links:
            link = loose.get('href')
            if link.startswith("http://systems.hscic.gov.uk/data/ods/datadownloads"):
                text, link = process_link(loose)
                resources.append(build_resource("", text, link))

    for k, cell_types in dataset['data'].iteritems():
        table = dom.xpath(k)[0]
        rows = table.cssselect('tr')[1:]

        for row in rows:
            date_pos = cell_types.get("date", -1)
            if date_pos != -1:
                date = row[cell_types["date"]].text_content().strip()

            for x in xrange(0, len(row)):
                if x == date_pos:
                    continue

                links = row[x].cssselect("a")
                if len(links) > 0:
                    # Ignore empty cells that are usefully provided.
                    text, link = process_link(links[0])

            resources.append(build_resource(date, text, link))

    metadata['resources'] = resources
    return [metadata]


def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    output_datasets = []
    for d in DATASETS:
        output_datasets.extend(process_dataset(d))

    metafile = DATA_DIR / "dataset.metadata.json"
    if metafile:
        metafile.truncate()
    metafile << json.dumps(output_datasets, indent=2)

    #for d in output_datasets:
    #    for r in d['resources']:
    #        hash = hashlib.sha224(r['url']).hexdigest()
    #        download_file(r['url'], os.path.join(DATA_DIR, hash))



    return 0
