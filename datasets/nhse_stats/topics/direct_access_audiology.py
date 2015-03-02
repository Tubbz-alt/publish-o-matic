""" Scraper for  http://www.england.nhs.uk/statistics/statistical-work-areas/direct-access-audiology/ """
import calendar
import datetime
import re

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom


ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/direct-access-audiology/daa-data/"


def date_range_from_string(s):
    m = re.match("(.*)\s(\d{4}).*", s)

    mnth = list(calendar.month_name).index(m.groups()[0])
    year = int(m.groups()[1])
    _, end = calendar.monthrange(year, mnth)
    mnth = str(mnth).zfill(2)

    return "{}-{}-01".format(year, mnth), "{}-{}-{}".format(year, mnth, end)


def scrape(workspace):
    print "Scraping Direct Access to Audiology with workspace {}".format(workspace)
    datasets = []

    html = requests.get(ROOT).content
    page = fromstring(html)

    desc = page.cssselect('h1')[1].getparent().getnext().text_content().strip()

    def is_header_div(d):
        return d is None or d.tag == 'h3' or\
            (d.tag == 'div' and len(d.cssselect('h3')) == 1)

    h3s = page.cssselect('h3')
    for h3 in h3s:
        title = h3.text_content().strip()
        container = []
        while h3 is not None:
            h3 = h3.getnext()
            if is_header_div(h3):
                break
            container.extend(h3.cssselect('a'))

        dataset = {
            "title": "Direct Access Audiology Data - {}".format(title),
            "resources": [anchor_to_resource(l) for l in container],
            "origin": ROOT,
            "notes": desc,
            "tags": ["audiology"],
        }
        s, e = date_range_from_string(title)
        dataset["coverage_start_date"] = s
        dataset["coverage_end_date"] = e
        dataset["name"] = slugify.slugify(dataset["title"]).lower()
        datasets.append(dataset)


    datasets = filter(lambda x: x is not None, datasets)
    return datasets