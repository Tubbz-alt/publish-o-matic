""" http://www.england.nhs.uk/statistics/statistical-work-areas/maternity-and-breastfeeding/ """

import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/maternity-and-breastfeeding/"

def scrape(workspace):
    print "Scraping Maternity and Breastfeeding with workspace {}".format(workspace)
    datasets = []

    page = fromstring(requests.get(ROOT).content)

    links = [a for a in page.cssselect('.center a') if 'upload' in a.get('href')]
    print len(links)

    dataset = {
        "title": "Maternity and Breastfeeding Data",
        "tags": ["maternity", "breastfeeding"],
        "resources": [anchor_to_resource(a) for a in links],
        "notes": "This collection reports on the number and proportion "\
                 "of women seen and assessed by a healthcare professional "\
                 "within 12 weeks and 6 days of their maternity, the number "\
                 "and proportion of mothers' who have initiated or not "\
                 "initiated breastfeeding and the number and proportion of "\
                 "infants who have been fully, partially or not at all breastfed "\
                 "at 6-8 weeks",
        "origin": ROOT,
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    print dataset
    return [dataset]
