"""
Scrape ODS data from the HSCIC
"""
import json
import sys

import ffs

sys.path.append(ffs.Path.here().parent)
import scrape

DATA_DIR = ffs.Path.here()/'../../data'

DOWNLOADS = 'http://systems.hscic.gov.uk/data/ods/datadownloads/index'

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

def check_sanity_of(metadata):
    """
    We've just finished scraping, let's make sure we haven't scraped bullshit.
    """
    for dataset in metadata:
        for resource in dataset['resources']:
            if not resource['url']:
                print dataset['title']
                print dataset['url']
                print resource
                raise Error('You scraped a resource without noting the URL Larry')
    return
        
def fetch_dataset_metadata(url):
    """
    Given a URL, fetch the metadata and resources
    from that page, and return it as a dict.
    """
    print url
    dom = scrape._astree(url)
    title = dom.cssselect('h1.documentFirstHeading')[0].text_content().strip()
    description_elements = [e.text_content() for e in dom.cssselect('#parent-fieldname-text')[0] if e.tag != 'table']
    description = "\n".join(description_elements).strip()

    metadata = dict(
        url=url,
        title=title,
        description=description,
    )
    resources = []

    try:
        data_tbody = dom.cssselect('table.listing tbody')[1]
    except IndexError: # Sometimes the table isn't built that way
        data_tbody = dom.cssselect('table.listing tbody')[0]
    resource_rows = data_tbody.cssselect('tr')

    try:
        for row in resource_rows:
            if 'haandsa' in url:
                try:
                    description, name, created, _ = row
                except ValueError:
                    description, name, created = row
            else:
                name, description, created = row
                
            # if 'safehaven' in url:
            #     import pdb;pdb.set_trace()
                
            resource = {
                'url': name.cssselect('a')[0].get('href'),
                'name': name.text_content().strip(),
                'description': description.text_content().strip()
            }
            resources.append(resource)
    except ValueError: # Sometimes there are more columns
        for row in resource_rows:
            name, full, excel, created = row
            resource = {
                'url': full.cssselect('a')[0].get('href'),
                'name': 'Full ' + name.text_content().strip(),
                'description': name.text_content().strip()
            }
            resources.append(resource)
            if excel.text_content().strip() == 'N/A':
                continue
            try:
                resource = {
                    'url': excel.cssselect('a')[0].get('href'),
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
    dom = scrape._astree(DOWNLOADS)

    downloads = dom.cssselect('table.listing a.internal-link')
    categories = list(set(a.get('href') for a in downloads))
    metadata = [fetch_dataset_metadata(url) for url in categories]

    check_sanity_of(metadata)
    
    metafile = DATA_DIR/'ods.json'
    metafile.truncate()
    metafile << json.dumps(metadata, indent=2)
    return 
        
def main():
    fetch_ods_metadata()
    return 0

if __name__ == '__main__':
    sys.exit(main())
