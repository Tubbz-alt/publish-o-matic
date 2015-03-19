"""
Scrape Prescribing
"""
import calendar
import json
import sys
import urllib

import ffs
import html2text
from lxml.html import fromstring, tostring
import re
import requests
import slugify

from publish.lib.metadata import get_resource_path
from publish.lib.helpers import filename_for_resource, download_file, get_dom, hd, to_markdown, anchor_to_resource
from publish.lib.upload import Uploader

ROOT = 'http://www.hscic.gov.uk/searchcatalogue?q=title:"GP+Practice+Prescribing+Data"&topics=0%2fPrescribing&sort=Relevance&size=10&page={}'

DATE_MATCH = re.compile("Date Range:\s(.*)\s(\d{2}),\s(\d{4})\sto\s(.*)\s(\d{2}),\s(\d{4})")
MONTHS = dict((v,str(k).zfill(2)) for k,v in enumerate(calendar.month_name))

def get_page_count():
    dom = get_dom(ROOT.format(1))
    return int(hd(dom.cssselect('#paging li a.last')).text_content())

def collect_urls(page_num):
    dom = get_dom(ROOT.format(page_num))
    return [a.get('href') for a in dom.cssselect('a.HSCICProducts')]

def get_date_range(dom):
    dr = dom.cssselect('.daterange')
    if len(dr) == 0:
        return "", ""
    txt = dr[0].text_content().strip()

    m = DATE_MATCH.match(txt)
    if not m:
        return "", ""

    g = m.groups()
    sdate = "{}-{}-{}".format(g[2], MONTHS[g[0]], g[1]).strip()
    edate = "{}-{}-{}".format(g[5], MONTHS[g[3]], g[4]).strip()
    return sdate, edate

def scrape_page(url):
    dom = get_dom(url)

    description = to_markdown(''.join([tostring(d) for d in dom.cssselect('.summary')]))

    resources = []
    for a in dom.cssselect('.notevalue a'):
        href = a.get('href')
        if 'searchcatalogue' in href or '.exe' in href:
            continue
        if not "datagov.ic.nhs.uk" in href:
            continue
        resources.append(anchor_to_resource(a))

    dataset = {
        "title": dom.cssselect('#headingtext')[0].text_content().strip(),
        "notes": description,
        "resources": resources,
        "tags": ['prescibing'],
        "frequency": "Monthly",
        "origin": url
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()[:99]

    sdate, edate = get_date_range(dom)
    dataset["coverage_start_date"] = sdate or ""
    dataset["coverage_end_date"] = edate or ""

    return dataset

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace)

    page_count = get_page_count()
    print "There are {} pages".format(page_count)

    urls = []
    for p in xrange(1, page_count + 1):
        urls.extend(collect_urls(p))
    print "Found {} urls".format(len(urls))

    datasets = []
    for url in urls:
        datasets.append(scrape_page(url))

    with open(DATA_DIR / "metadata.json", 'w') as f:
        json.dump(datasets, f)

