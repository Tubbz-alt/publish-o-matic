"""
Scraper for
http://www.england.nhs.uk/statistics/statistical-work-areas/mental-health-community-teams-activity/
"""
import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource

def date_range_for_year(year):
    s = "{}-04-01".format(year)
    e = "{}-03-30".format(year+1)
    return s, e

def process_para(para, notes):
    title = para.cssselect('strong')[0].text_content()
    if 'CSV Format' in title:  # We'll take the XLS version for now.
        return None

    dataset = {}

    part = title.encode('utf8')[0:7].replace('/', '-')
    s, e = "", ""
    if part == 'England':
        part = 'England Time Series'
    else:
        s, e = date_range_for_year(int(part[0:4]))
    dataset['coverage_start_date'] = s
    dataset['coverage_end_date'] = e

    dataset["title"] = "Mental Health Community Teams Activity - {}".format(part)
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    dataset["origin"] = "http://www.england.nhs.uk/statistics/statistical-work-areas/mental-health-community-teams-activity/"
    dataset["notes"] = notes
    dataset['groups'] = ['mhc']
    links = para.cssselect('a')
    dataset['resources'] = [anchor_to_resource(l) for l in links]

    return dataset



def scrape(workspace):
    print "Scraping MSA with workspace {}".format(workspace)

    datasets = []

    page = requests.get("http://www.england.nhs.uk/statistics/statistical-work-areas/mental-health-community-teams-activity/")
    html = fromstring(page.content)

    center = html.cssselect('.column.center')[0]

    h3s = list(center.cssselect('H3'))
    p = filter(lambda x: x.text_content().startswith('Background'), h3s)[0]

    desc = []
    while True:
        p = p.getnext()
        if not p.tag == 'p':
            break
        desc.append(p.text_content())
    notes = to_markdown(''.join(desc))

    guidance = filter(lambda x: x.text_content().startswith('Guidance'), h3s)[0].getnext().cssselect('a')[0]
    r = anchor_to_resource(guidance)

    data = filter(lambda x: x.text_content().startswith('Data'), h3s)[0]
    paras = []
    while True:
        data = data.getnext()
        if not data.tag == 'p':
            break
        paras.append(data)

    datasets.extend([process_para(p, notes) for p in paras])

    datasets = filter(lambda x: x is not None, datasets)
    # Insert the guidance into each dataset
    for dataset in datasets:
        dataset['resources'].insert(0, r)

    datasets = sorted(datasets, key=lambda x:x['title'])
    print datasets
    return datasets
