""" Scrapes the Annual Imaging and Radiodiagnostics Data at
http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/imaging-and-radiodiagnostics-annual-data/
"""

import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource

def process(page, url):
    desc = "Annual Imaging and Radiodiagnostics data relate to the number of imaging "\
           "and radiological examinations or tests carried out in the NHS in England "\
           "during each year. Data for this collection is available back to 1995-96."
    title = "Annual Imaging and Radiodiagnostics Data"
    dataset = {
        "title": title,
        "name": slugify.slugify(title).lower(),
        "origin": url,
        "notes": desc,
        "resources": [],
        "groups": ['aird'],
    }

    links = page.cssselect('.center p a')
    for link in links:
        href = link.get('href')
        ext = href[-3:]
        if ext in ['xls', 'doc', 'pdf']:
            dataset['resources'].append(anchor_to_resource(link))

    return dataset

def scrape(workspace):
    print "Scraping AIRD with workspace {}".format(workspace)
    datasets = []

    url = "http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/diagnostics-census-data/"
    html = requests.get(url).content
    page = fromstring(html)

    datasets.append(process(page, url))

    datasets = filter(lambda x: x is not None, datasets)
    return datasets