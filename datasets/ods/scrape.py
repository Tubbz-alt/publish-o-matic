"""
Scrape ODS data from the HSCIC
"""
import json
import os
import sys
import urllib

import ffs
from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import download_file, to_markdown, remove_tables_from_dom



DATA_DIR = None

DOWNLOADS = 'http://systems.hscic.gov.uk/data/ods/datadownloads/index'

class Error(Exception):
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

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

def check_sanity_of(metadata):
    """
    We've just finished scraping, let's make sure we haven't scraped bullshit.
    """
    for dataset in metadata:
        seen = []
        new_resources = []
        for resource in dataset['resources']:
            if resource['url'] in seen:
                continue
            seen.append(resource['url'])

            new_resources.append(resource)
        dataset['resources'] = new_resources

    print len(dataset['resources'])

def fetch_dataset_metadata(url):
    """
    Given a URL, fetch the metadata and resources
    from that page, and return it as a dict.
    """
    print "Scraping", url

    dom = _astree(url)
    title = dom.cssselect('h1.documentFirstHeading')[0].text_content().strip()

    # We can't strip the tables out of the full-dom because we want to get the resources.
    # For now we'll build a new DOM using the HTML we want.
    desc_html = tostring(dom.cssselect('#parent-fieldname-text')[0])
    desc_dom = fromstring(desc_html)
    remove_tables_from_dom(desc_dom)
    description = to_markdown(tostring(desc_dom))

    metadata = dict(
        url=url,
        title=title,
        description=description,
        name=slugify.slugify(title).lower()
    )
    resources = []
    appended_urls = []
    resource_rows = dom.cssselect('table.listing tbody tr')
    resource_rows = [r for r in resource_rows if r.text_content().find('File Description') == -1]

    try:
        for row in resource_rows:

            if 'haandsa' in url:
                try:
                    description, name, created, _ = row
                except ValueError:
                    description, name, created = row
            else:
                name, description, created = row

            resource = {
                'url': name.cssselect('a')[0].get('href'),
                'name': name.text_content().strip(),
                'description': description.text_content().strip()
            }

            if resource['url'] in appended_urls:
                print "Already have a resource pointing to {}".format(resource['url'])
                continue
            appended_urls.append(resource['url'])

            resources.append(resource)
    except ValueError: # Sometimes there are more columns
        for row in resource_rows:
            excel = None

            print len(row), [r.text_content() for r in row]
            if len(row) == 4:
                name, full, excel, created = row
            elif len(row) == 3:
                name, full, created = row

            resource = {
                'url': full.cssselect('a')[0].get('href'),
                'name': 'Full ' + name.text_content().strip(),
                'description': name.text_content().strip()
            }
            resources.append(resource)
            if excel is not None and excel.text_content().strip() == 'N/A':
                continue

            url = full.cssselect('a')[0].get('href')
            if excel is not None:
                url = excel.cssselect('a')[0].get('href')

            if url in appended_urls:
                print "Already have a resource pointing to {}".format(url)
                continue

            appended_urls.append(url)
            try:
                resource = {
                    'url': url,
                    'name': 'Excel ' + name.text_content().strip(),
                    'description': name.text_content().strip()
                }
            except IndexError:
                import pdb;pdb.set_trace()
                print row
            resources.append(resource)

    metadata['resources'] = resources
    return metadata

def fetch_ods_metadata():
    """
    * Fetch the list of downloads from the download index
    * Iterate through them gathering metadata on each
    * Write to a file as one dataset per "Download"
    """
    dom = _astree(DOWNLOADS)

    downloads = dom.cssselect('table.listing a.internal-link')

    # Get a list of URLs to detail pages, there are duplicates.
    categories = list(set(a.get('href') for a in downloads))

    #metadata = [fetch_dataset_metadata(categories[4])]
    metadata = [fetch_dataset_metadata(url) for url in categories]
    check_sanity_of(metadata)
    metafile = DATA_DIR/'dataset.metadata.json'
    if metafile:
        metafile.truncate()
    metafile << json.dumps(metadata, indent=2)
    print "Wrote metadata file to ", metafile

def fetch_ods_data():
    """
    Given the metadata we've scraped from ODS, let's now download the
    data files!
    """
    metafile = DATA_DIR/'dataset.metadata.json'
    metadata = metafile.json_load()
    for dataset in metadata:
        downloaded = []

        dataset_dir = DATA_DIR / dataset['name']
        dataset_dir.mkdir()

        for resource in dataset['resources']:
            parts = resource['url'].split('/')
            if parts[-2] == 'xls':
                target = os.path.join(dataset_dir, "xls_{}".format(parts[-1]) )
            else:
                target = os.path.join(dataset_dir, parts[-1] )

            if resource['url'] in downloaded:
                print "Recently downloaded {} so not downloading again".format(resource['url'])
                continue
            print "Fetching {}".format(resource['url'])
            download_file(resource['url'], target)

            downloaded.append(resource['url'])
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    fetch_ods_metadata()
    fetch_ods_data()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
