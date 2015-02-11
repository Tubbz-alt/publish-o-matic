
import ffs
import requests
from lxml.html import fromstring

DATA_DIR = None
ROOT_URL = "http://www.england.nhs.uk/statistics/statistical-work-areas/"

def is_upload_url(url):
    return url.startswith('http://www.england.nhs.uk/statistics/wp-contents/uploads')

def scrape():
    html = requests.get(ROOT_URL).content
    page = fromstring(html)
    blocks = page.cssselect('.column.center p')
    for block in blocks[1:]:
        anchor = block.cssselect('strong a')
        if not len(anchor):
            anchor = block.cssselect('a')

        link = anchor[0].get('href')
        print link

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    scrape()

    return 0
