""" Diagnostic Imaging Dataset """

import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

FULL_DESC = None
ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostic-imaging-dataset/"

def get_description(dom):
    h = dom.cssselect('h1')[1].getparent().getnext()
    desc = []

    while True:
        if h.tag not in ['p', 'ul']:
            break
        desc.append(tostring(h))
        h = h.getnext()
    return to_markdown("".join(desc))

def year_range_from_title(title):
    years_match = re.match('.*(\d{4})\-(\d{2}).*(\d{4})\-(\d{2}).*', title)
    if years_match:
        groups = years_match.groups()
        syear = groups[0]
        eyear = groups[-1]
        eyear = str(syear)[0:2] + str(eyear)
        return int(syear), int(eyear)

    years_match = re.match('.*(\d{4})[-/](\d{2}).*', title)
    if not years_match:
        return None, None
    syear = int(years_match.groups()[0])
    return syear, syear + 1

def scrape_page(url, title=None):
    global FULL_DESC
    page = get_dom(url)

    if FULL_DESC is None:
        FULL_DESC = get_description(page)

    links = [a for a in page.cssselect('.center a') if 'upload' in a.get('href')]
    dataset = {
        "title": title or page.cssselect('h1')[1].text_content().strip(),
        "notes": FULL_DESC,
        "origin": url,
        "tags": ["diagnostic imaging"],
        "resources": [anchor_to_resource(l) for l in links],
        "groups": ['did']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    syear, eyear = year_range_from_title(dataset["title"])
    if syear and eyear:
        dataset["coverage_start_date"] = "{}-04-01".format(syear)
        dataset["coverage_end_date"] = "{}-03-31".format(eyear)
    return dataset

def scrape(workspace):
    print "Scraping Diagnostic Imaging Data with workspace {}".format(workspace)

    datasets = []

    page = get_dom(ROOT)
    datasets.append(scrape_page(ROOT, title="Diagnostic Imaging Dataset - Previous versions"))

    h3 = hd([h for h in page.cssselect('h3') if h.text_content().strip() == "Data"])
    for a in h3.getnext().cssselect('a'):
        datasets.append(scrape_page(a.get('href')))

    datasets = filter(lambda x: x is not None, datasets)
    return datasets