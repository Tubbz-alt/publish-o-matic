""" VTE scraper """
import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/vte/"


def get_description(h1):
    """ From the header, read the description until we get either:
        a. A non-p or ul tag
        b. An element that contains a link with 'Guidance' in the text
    """
    p = h1.getnext()
    if p is None:
        p = h1.getparent().getnext()

    desc = []
    while True:
        if not p.tag in ['p', 'ul']:
            break
        glink = p.cssselect('a')
        if len(glink) > 0 and 'Guidance' in glink[0].text_content():
            break
        desc.append(tostring(p))
        p = p.getnext()

    return to_markdown("\n".join(desc))

def year_range_from_title(title):
    years_match = re.match('.*(\d{4})\-(\d{2}).*(\d{4})\-(\d{2}).*', title)
    if years_match:
        groups = years_match.groups()
        syear = groups[0]
        eyear = groups[-1]
        eyear = str(syear)[0:2] + str(eyear)
        return int(syear), int(eyear)

    years_match = re.match('.*(\d{4})[-/](\d{2}).*', title)
    syear = int(years_match.groups()[0])
    return syear, syear + 1

def scrape_page(url):
    """ Scrapes a single page to create a dataset """

    print "Scraping ", url
    page = get_dom(url)
    header = page.cssselect('h1')[1]

    title = header.text_content().strip().replace('/', '-')
    description = get_description(header)

    links = [a for a in page.cssselect('.center a') if 'upload' in a.get('href')]
    resources = [anchor_to_resource(l) for l in links]

    start_year, end_year = year_range_from_title(title)

    dataset = {
        "title": title,
        "notes": description,
        "resources": resources,
        "origin": url,
        "coverage_start_date": "{}-04-01".format(start_year),
        "coverage_end_date": "{}-03-31".format(end_year),
        "tags": ["VTE"],
        "groups": ["vte"]
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    print dataset["name"], " has ", len(dataset["resources"]), " resources"
    return dataset

def scrape(workspace):
    print "Scraping VTE with workspace {}".format(workspace)

    datasets = []

    page = get_dom(ROOT)
    pages = page.cssselect('h4 a')
    for p in pages:
        datasets.append(scrape_page(p.get('href')))


    datasets = filter(lambda x: x is not None, datasets)
    print "Found", len(datasets)
    return datasets