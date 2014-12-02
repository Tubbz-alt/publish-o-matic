"""
I guess this is a package now.
"""
from lxml.html import fromstring
import requests

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
