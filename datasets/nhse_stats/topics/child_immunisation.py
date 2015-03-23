""" Child immunisation data """

import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, hd
from publish.lib.encoding import fix_bad_unicode

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/child-immunisation/"

QUARTERS = {
    1: (4,  6),
    2: (7, 9),
    3: (10, 12),
    4: (1,  3),
}


def get_quarter_and_year(s):
    # Child Immunisation 2014/15 Q2 V2 (XLS, 944KB)
    m = re.match(".*(\d{4}).*(\d{2}).*Q(\d).*", s)
    if not m:
        return 9999, 4

    return int(m.groups()[0]), int(m.groups()[1])

def scrape(workspace):
    print "Scraping Child Immunisation with workspace {}".format(workspace)

    html = requests.get(ROOT).content
    page = fromstring(html)

    div = page.cssselect('.center')[0]
    links = div.cssselect('a')[3:]

    h3 = hd([h for h in div.cssselect('h3') if h.text_content().strip() == "Background"])
    desc = h3.getnext().text_content()

    dataset = {
        "title": "Child Immunisation",
        "notes": to_markdown(fix_bad_unicode(unicode(desc))),
        "coverage_start_date": "",
        "coverage_end_date": "",
        "resources": [],
        "frequency": "Quarterly",
        "origin": ROOT,
        "tags": ["immunisation", "children"],
        "groups": ['child_immunisation']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    earliest_quarter, earliest_year = 4, 9999
    latest_quarter, latest_year = 1, 2000

    for l in links:
        y, q = get_quarter_and_year(l.text_content().strip())
        if y < earliest_year:
            earliest_year = y
            if q < earliest_quarter:
                earliest_quarter = q
        if y > latest_year:
            latest_year = y
            if latest_quarter > q:
                latest_quarter = q

        dataset["resources"].append(anchor_to_resource(l))

    if earliest_quarter == 4:
        earliest_year += 1
    if latest_quarter == 4:
        latest_year += 1
    s, e = QUARTERS[earliest_quarter]
    dataset["coverage_start_date"] = "{}-{}-01".format(earliest_year, str(s).zfill(2))
    s, e = QUARTERS[latest_quarter]
    _, last_day = calendar.monthrange(latest_year, s-1)
    dataset["coverage_end_date"] = "{}-{}-{}".format(earliest_year, str(s-1).zfill(2), last_day)

    return [dataset]