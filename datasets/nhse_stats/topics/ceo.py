"""
Scrapes the Cancelled Elective Operations data available at
http://www.england.nhs.uk/statistics/statistical-work-areas/cancelled-elective-operations/cancelled-ops-data/
"""

import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource


ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/cancelled-elective-operations/cancelled-ops-data/"
#MONTH_DATE_RANGE_RE = re.compile(".*,\s(.*)\sto\s(.*)\s(\d{4}).*")
#DATE_RANGE_RE = re.compile(".*Q(\d)\s(\d{4}).*(\d{2})")
MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))


"""
def month_to_month_from_title(title):
    # Cancer Waiting Times, April to June 2012 - Provider Based
    m = MONTH_DATE_RANGE_RE.match(title)
    if not m:
        print "Not a month range string..."
        return "", ""

    startm = MONTHS_LOOKUP[m.groups()[0]]
    endm = MONTHS_LOOKUP[m.groups()[1]]
    year = int(m.groups()[2])
    _, mend = calendar.monthrange(year, endm)

    start = "{}-{}-{}".format(year, str(startm).zfill(2), 1)
    end   = "{}-{}-{}".format(year, str(endm).zfill(2), str(mend).zfill(2))
    return start, end


def date_range_from_title(title):
    # Commissioner-based Cancer Waiting Times for Q3 2014-15
    m = DATE_RANGE_RE.match(title)
    if not m:
        return month_to_month_from_title(title.encode('utf8'))

    quarters = {
        1: (4,  6),
        2: (7, 9),
        3: (10, 12),
        4: (1,  3),
    }

    qstart, qend = quarters[int(m.groups()[0])]
    yearstart = m.groups()[1]

    # fix in 2090 something before the rollover ...
    yearend = int("{}{}".format(yearstart[0:2], m.groups()[2]))
    yearstart = int(yearstart)
    _, mend = calendar.monthrange(yearend, qend)

    s = "{}-{}-01".format( yearstart, str(qstart).zfill(2))
    e = "{}-{}-{}".format( yearend, str(qend).zfill(2), mend)

    print s, e

    return s, e


    dataset['title'] = title
    dataset['name'] = slugify.slugify(title).lower()
    dataset["notes"] = to_markdown( tostring(div.cssselect('article p')[0]) )
    dataset["tags"] = ["CWT"]
    dataset["resources"] = resources
    dataset["origin"] = link.get('href')
    if drs:
        dataset["coverage_start_date"] = drs
    if dre:
        dataset["coverage_end_date"] = dre
    dataset["frequency"] = "Quarterly"
"""

ROOT_TITLE = 'Cancelled Elective Operations Data - {}'

def years_to_date_range(years):

    m = re.match('(\d{4}).*(\d{2})', years)
    if not m:
        return years, "", ""

    syear = m.groups()[0]
    eyear = "{}{}".format(syear[0:2], m.groups()[1])

    new_year_string = "{}-{}".format(syear, eyear)

    start_date = "{}-04-01".format(syear)
    end_date = "{}-03-31".format(eyear)

    return new_year_string, start_date, end_date


def process_dataset(title, links, notes):
    dataset = {}

    year_string, start, end = years_to_date_range(title)

    dataset['title'] = ROOT_TITLE.format(year_string)
    dataset['name'] = slugify.slugify(dataset['title']).lower()
    dataset['coverage_start_date'] = start
    dataset['coverage_end_date'] = end
    dataset['notes'] = notes
    dataset['origin'] = ROOT
    dataset['resources'] = [anchor_to_resource(r) for r in links]
    dataset['tags'] = ['elective']
    return dataset

def scrape(workspace):
    print "Scraping Cancelled Elective Ops with workspace {}".format(workspace)
    datasets = []

    html = requests.get(ROOT).content
    page = fromstring(html)
    div = page.cssselect('.center')[0]

    desc = []
    start = div.cssselect('p')[0]
    desc.append(tostring(start))

    stop = False
    while not stop:
        start = start.getnext()
        if len(start.cssselect('strong')) > 0:
            stop = True
            break
        desc.append(tostring(start))

    notes = to_markdown(''.join(desc)).encode('utf8')

    latest_links = []

    current_title = None
    links = []
    while start is not None:
        if len(start.cssselect('strong')) > 0:
            # New title, process existing block
            if links and current_title:
                if current_title == "Latest Data":
                    latest_links = links[:]
                else:
                    datasets.append(process_dataset(current_title, links, notes))
            links = []
            current_title = start.cssselect('strong')[0].text_content()

        links.extend(start.cssselect('a'))
        start = start.getnext()

    if links:
        datasets.append(process_dataset(current_title, links, notes))


    to_present = latest_links[-1]
    ds_latest = process_dataset("Time Series", [to_present], notes)
    ds_latest['coverage_start_date'] = '1994-04-01'
    datasets.append(ds_latest)

    for link in latest_links[0:-1]:
        resource = anchor_to_resource(link)
        m = re.match('.*(\d{2})/(\d{2}).*', resource['description'])
        year_range = "20{}-20{}".format(m.groups()[0], m.groups()[1])

        for ds in datasets:
            if year_range in ds['name']:
                ds['resources'].insert(0, resource)


    datasets = filter(lambda x: x is not None, datasets)
    return datasets


