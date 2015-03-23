""" Archived flu data
http://webarchive.nationalarchives.gov.uk/20130107105354/http://www.dh.gov.uk/en/Publicationsandstatistics/Statistics/Performancedataandstatistics/DailySituationReports/index.htm
"""
import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

ROOT = "http://webarchive.nationalarchives.gov.uk/20130107105354/http://www.dh.gov.uk/en/Publicationsandstatistics/Statistics/Performancedataandstatistics/DailySituationReports/index.htm"
DESCRIPTION = None

def scrape_block(block, title):
    global DESCRIPTION

    dataset = {
        "title": title,
        "notes": DESCRIPTION,
        "tags": ["sitrep", "winter"],
        "origin": ROOT,
        "resources": [anchor_to_resource(a) for a in block.cssselect('.itemLinks li a')],
        "groups": ['winter']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    for r in dataset["resources"]:
        r['description'] = r['description'].replace('Download ', '')
    return dataset

def scrape(workspace):
    print "Scraping Archived Flu Data with workspace {}".format(workspace)
    global DESCRIPTION
    datasets = []

    page = get_dom(ROOT)

    DESCRIPTION = to_markdown(unicode(page.cssselect('.introText')[0].text_content().strip()))

    containers = page.cssselect('.itemContainer')[1:]
    datasets.append(scrape_block(containers[0], "Daily Hospital Situation Report 2011-12"))
    datasets.append(scrape_block(containers[1], "Daily Hospital Situation Report 2010-11"))
    datasets.append(scrape_block(containers[2], "Daily Flu Situation Report 2010-11"))
    datasets.append(scrape_block(containers[3], "Daily SitRep Guidance 2011-12"))

    datasets = filter(lambda x: x is not None, datasets)
    print "Found {} datasets".format(len(datasets))
    return datasets