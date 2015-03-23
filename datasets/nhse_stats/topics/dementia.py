"""
Dementia stats scraper
This scraper looks a LOT like the VTE scraper, and so we'll just import the
functions from there
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

from datasets.nhse_stats.topics.vte import get_description, year_range_from_title, scrape_page

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/dementia/"


def scrape(workspace):
    print "Scraping Dementia stats with workspace {}".format(workspace)

    datasets = []

    page = get_dom(ROOT)
    pages = page.cssselect('.center h3 a')
    for p in pages:
        ds = scrape_page(p.get('href'))
        ds["groups"] = ['dementia']
        datasets.append(ds)


    datasets = filter(lambda x: x is not None, datasets)
    return datasets