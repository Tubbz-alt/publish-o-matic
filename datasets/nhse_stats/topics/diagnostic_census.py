""" Diagnotic Census Data from http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/diagnostics-census-data/ """

import calendar
import datetime
import re

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom


ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/diagnostics-census-data/"

def process_para(para, desc):
    links = para.cssselect('a')
    if len(links) == 0:
        return None

    if len(para.getnext().cssselect('strong')) == 0:
        links.extend(para.getnext().cssselect('a'))

    m = re.match('(\d{4})-(\d{2})', para.cssselect('strong')[0].text_content())
    years = m.groups()[0]
    yeare = years[:2] + m.groups()[1]

    dataset = {
        "title": "Quarterly Diagnostic Waiting Times {}-{}".format(years, yeare),
        "origin": ROOT,
        "tags": ["waiting times"],
        "notes": desc
    }
    dataset["coverage_start_date"] = "{}-04-01".format(years)
    dataset["coverage_end_date"] = "{}-03-31".format(yeare)
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    dataset["resources"] = [anchor_to_resource(l) for l in links]

    return dataset

def scrape(workspace):
    print "Scraping Diagnostic Census with workspace {}".format(workspace)
    datasets = []

    dom = get_dom(ROOT)
    paras = dom.cssselect('p strong')
    paras = [p for p in sorted(paras, reverse=True) if p.text_content().strip().startswith('20')]

    notes = "The quarterly diagnostics census collects data on patients waiting over 6 weeks "\
            "for a diagnostic test. Unlike the monthly data, the quarterly census includes "\
            "patients waiting over 6 weeks for all diagnostic tests and not just the key 15 "\
            "tests. Data is collected from NHS Trusts and independent sector providers treating "\
            "NHS patients. Data for this collection is available back to Feb-06"

    for p in paras:
        datasets.append(process_para(p.getparent(), notes))

    datasets = filter(lambda x: x is not None, datasets)
    return datasets
