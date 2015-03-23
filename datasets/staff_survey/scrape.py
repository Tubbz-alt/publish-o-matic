"""
Staff survey scraper for http://www.nhsstaffsurveys.com/
"""

import json
import re
import requests
from urlparse import urljoin

import ffs
from lxml.html import fromstring, tostring
from publish.lib.helpers import anchor_to_resource, to_markdown, get_dom, hd, tl
import slugify

ROOT = "http://www.nhsstaffsurveys.com/"

def scrape_page(page, url):
    dataset = {
        "title": "NHS {}".format(hd(page.cssselect('h1')).text_content().strip()),
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    dataset["origin"] = url
    dataset["tags"] = ["staff survey"]

    year = re.match('.*(\d{4}).*', dataset['title']).groups()[0]
    dataset["coverage_start_date"] = "{}-01-01".format(year)
    dataset["coverage_end_date"] = "{}-12-31".format(year)

    desc_node = page.cssselect('div.column-content p')
    if desc_node:
        dataset["notes"] = hd(desc_node).text_content()
    else:
        dataset["notes"] = "Results for the Staff Survey {year} can be seen below. "\
                           "We have released detailed spreadsheets showing key finding "\
                           "and question level information for each trust who took part "\
                           "in the {year} survey.".format(year=year)
    dataset['notes'] = to_markdown(dataset['notes'])
    dataset["resources"] = []

    boxes = page.cssselect('.document-box')
    for box in boxes:
        a = box.cssselect('a')[0]
        resource = anchor_to_resource(a)
        resource['description'] = box.cssselect('h4')[0].text_content().strip()
        resource['url'] = urljoin(ROOT, resource['url'])
        dataset["resources"].append(resource)

    key = hd([a for a in page.cssselect('a') if a.text_content().strip() == 'Click here'])
    if key is not None:
        resource = anchor_to_resource(key)
        resource['description'] = "Key Findings"
        resource['url'] = urljoin(ROOT, resource['url'])
        dataset["resources"].append(resource)

    return dataset

def history(page):
    link = hd(hd(page.cssselect('#ctlNavigationPastResults')).cssselect('a'))
    page = get_dom(urljoin(ROOT, link.get('href')))

    div = hd(page.cssselect('.foldout-set'))
    links = [a for a in div.cssselect('a')
             if 'Detailed Spreadsheets' in a.text_content().strip()]
    for link in links:
        u = urljoin(ROOT, link.get('href'))
        page = get_dom(u)
        yield scrape_page(page, u)

def latest(page):
    # Find the Latest Data link at "http://www.nhsstaffsurveys.com/" and scrape
    # that page.
    link = hd(hd(page.cssselect('#ctlNavigationLatestResults')).cssselect('a'))
    page = get_dom(urljoin(ROOT, link.get('href')))

    h3 = hd([h for h in page.cssselect('h3') if h.text_content().strip() == "Detailed spreadsheets"])
    latest_link = hd(h3.getparent().getnext().cssselect('a'))

    u = urljoin(ROOT, latest_link.get('href'))
    page = get_dom(u)

    return scrape_page(page, u)

def main(workspace):
    data_dir = ffs.Path(workspace) / 'data'
    data_dir.mkdir()

    page = get_dom(ROOT)

    datasets = []
    datasets.append(latest(page))
    datasets.extend(history(page))

    datasets = filter(lambda x: x is not None, datasets)
    datasets.sort()

    print "Processed {} datasets".format(len(datasets))
    json.dump(datasets, open(data_dir / 'metadata.json', 'w'))



