""" Scrapes the data at
http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/monthly-diagnostics-waiting-times-and-activity/
 """

import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource

MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))

def _chunky(l):
    for i in xrange(0, len(l), 2):
        yield l[i:i+2]

def date_range_from_string(s):
    m, y = s.split(' ')

    m = MONTHS_LOOKUP[m]
    _, mend = calendar.monthrange(int(y), m)

    return "{}-{}-01".format(y,m), "{}-{}-{}".format(y, m ,mend)

def month(url, desc):
    datasets = []
    print "-->", url
    html = requests.get(url).content
    page = fromstring(html)

    links = filter(lambda x: x.text_content().strip().startswith('Monthly'), page.cssselect('.center p a'))

    for first, second in _chunky(links):
        when = re.match('.*\s(.*?\s\d{4}?).*\(.*', first.text_content().strip())
        dataset = {
            "title": "Monthly Diagnostics Data - {}".format(when.groups()[0]),
            "origin": url,
            "tags": ["statistics", "diagnostics"],
            "notes": desc,
        }
        dataset["name"] = slugify.slugify(dataset["title"]).lower()
        dataset["coverage_start_date"],dataset["coverage_end_date"] = date_range_from_string(when.groups()[0])
        dataset['resources'] = [anchor_to_resource(r) for r in [first,second]]
        datasets.append(dataset)

    return datasets

def monthly(page, desc):
    datasets = []
    h3s = page.cssselect('h3')
    h3 = filter(lambda x: x.text_content().strip() == "Data", h3s)[0]
    urls = [a.get('href') for a in h3.getnext().cssselect('a')]
    urls = filter(lambda x: not 'webarchive' in x,urls)
    urls.reverse()
    for u in urls:
        datasets.extend(month(u, desc))
    return datasets

def guidance(page):
    dataset = {
        "title": "Monthly Diagnostic Waiting Times and Activity - Guidance and Documentation",
        "origin": "http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/monthly-diagnostics-waiting-times-and-activity/",
        "tags": ["waiting times", "statistics"],
        "notes": ""
    }
    dataset['name'] = slugify.slugify(dataset['title']).lower()

    h3s = page.cssselect('h3')
    h3 = filter(lambda x: x.text_content().strip() == "Guidance and Documentation", h3s)[0]
    links = h3.getnext().cssselect('a')
    dataset['resources'] = [anchor_to_resource(l) for l in links]

    p = filter(lambda x: x.text_content().strip() == "Background", h3s)[0]
    desc = []
    while True:
        p = p.getnext()
        if p.tag != 'p':
            break
        desc.append(tostring(p))
    desc = desc[:-1]
    dataset['notes'] = to_markdown(''.join(desc))

    return dataset

def scrape(workspace):
    print "Scraping MDD with workspace {}".format(workspace)
    datasets = []

    url = "http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/monthly-diagnostics-waiting-times-and-activity/"
    html = requests.get(url).content
    page = fromstring(html)

    datasets.append(guidance(page))
    datasets.extend(monthly(page, datasets[0]['notes']))

    datasets = filter(lambda x: x is not None, datasets)
    return datasets