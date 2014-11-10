"""
Scrape US obesity datas.
"""
import json
import shutil
import sys
import urllib

import ffs
from lxml.html import fromstring
import requests
from slugify import slugify

DATA_DIR = ffs.Path.here()/'../data'
HEALTHINDICATORS = DATA_DIR/'healthindicators'
HEALTHINDICATORS.mkdir()
HEALTHINDICATORS_URL = 'http://www.healthindicators.gov/Indicators/Search?Query=obesity'


class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

        
class Dataset(object):
    def __init__(self, title, url, description, tags):
        self.title = title
        self.url = url
        self.description = description
        self.tags = tags

    @property
    def as_json(self):
        data = dict(title=self.title, url=self.url, description=self.description, tags=self.tags)
        return json.dumps(data, indent=2)

def _astree(url):
    """
    Helper that returns a URL as a lxml tree
    """
    content = urllib.urlopen(url).read()
    dom = fromstring(content)
    dom.make_links_absolute(url)
    return dom

def health_indicators_dataset(links):
    """
    Scrape the data from the dataset page.
    """
    for dataset in links:
        base_dom = _astree(dataset)
        title = base_dom.cssselect('h1')[0].text_content().strip()
        print '~~~~ Processing {0} Indicator "Warehouse" ~~~~'.format(title)

        description = base_dom.cssselect(
            '#PageContent')[0].text_content().split('\n')
        description = "\n".join([l.strip() for l in description if l.strip()])

        tags = [a.text_content().strip() for a in
                base_dom.cssselect('.TagCloud a span.VariableWidth')]
        url = dataset
        
        resourceslink = base_dom.cssselect(
            '#ctl00_ctl00_ctl00_subNavigation_subNavigation_downloadLink')[0]
        resourceslink = resourceslink.get('href')
        data={
            'ctl00_ctl00_ctl00_ctl14_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:4ae4914f-8c8e-4123-9d05-414d87b48357:ea597d4b:b25378d2;Telerik.Web.UI, Version=2014.1.225.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:fe3df733-ee56-4563-8789-bc399360084a:16e4e7cd:f7645509:24ee1bba:92fe8ea0:fa31b949:19620875:874f8ea2:f46195d3:490a9d4e:bd8f85e4;AjaxControlToolkit, Version=3.0.20820.16598, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:707835dd-fa4b-41d1-89e7-6df5d518ffb5:b14bb7d5:dc2d6e36:5acd2e8e:13f47f54:4cda6429:35ff259d:b80820f8:34018309;',
                '__VIEWSTATE': base_dom.cssselect('input[name="__VIEWSTATE"]')[0].value,
                '__VIEWSTATEGENERATOR': '53FFB31C',
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': 1,
                '__EVENTTARGET': 'ctl00$ctl00$ctl00$pageContent$pageContent$pageContent$btnDownload',
                '__EVENTARGUMENT': None,
                '__LASTFOCUS': None,

                'ctl00$ctl00$ctl00$ctl15$searchTextBox': 'Search for Indicators',
                'ctl00$ctl00$ctl00$ctl15$searchTextBoxValidatorRFVExtender_ClientState': None,
                'ctl00$ctl00$ctl00$shareButton$urlTextBox': dataset + '/Download',
                'ctl00_ctl00_ctl00_subNavigation_subNavigation_ctl02_ClientState': None,
                'ctl00$ctl00$ctl00$pageContent$pageContent$pageContent$fileTypeDDL':'CSV',
                'ctl00$ctl00$ctl00$pageContent$pageContent$pageContent$localeLevelDDL': 'National',
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': 1
        }
        print data
        resp = requests.post(
            resourceslink,
            data=data,
            stream=True
        )

        if resp.status_code != 200:
            raise Exception('Requesting dataset error')
        if resp.headers['content-type'].startswith('text/html'):
            import pdb; pdb.set_trace()
            raise Exception('Not a zip file error')

        import pdb; pdb.set_trace()
        resp.raw.decode_content = True

        ds = Dataset(title, url, description, tags)

        tmp = ffs.Path.newdir()
        zipfile = tmp/'download.zip'
        
        with zipfile.open('wb') as fh:
            shutil.copyfileobj(resp.raw, fh)

        zipfile = zipfile.as_zip
        extracted = tmp/'extracted'
        extracted.mkdir()

        print extracted
        print zipfile
        
        zipfile.extract(extracted)

        target = HEALTHINDICATORS/slugify(title)
        target.mkdir()

        for i in extracted.ls():
            print i
            dest = target/i[-1]
            moved = i.mv(dest)

        metadata = target/'metadata.json'
        metadata << ds.as_json
    return
        
def health_indicators_warehouse():
    """
    Grab everything from the health indicator warehouse tagged Obesity.
    """
    print '~~~~ Fetching master dataset list from Indicator "Warehouse" ~~~~'
    content = urllib.urlopen(HEALTHINDICATORS_URL).read()
    base_dom = fromstring(content)
    base_dom.make_links_absolute(HEALTHINDICATORS_URL)
    links = [a.get('href') for a in base_dom.cssselect('.IndicatorResultsList a') 
             if a.get('href').startswith('http://')]
    health_indicators_dataset(links)
    return

def main():
    health_indicators_warehouse()
    return 0

if __name__ == '__main__':
    sys.exit(main())
