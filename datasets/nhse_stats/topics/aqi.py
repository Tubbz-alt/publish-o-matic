"""
Scrapes the ambulance quality indicators at
http://www.england.nhs.uk/statistics/statistical-work-areas/ambulance-quality-indicators/
"""
import calendar
import datetime
import re
import ffs

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/ambulance-quality-indicators/"


DATE_RANGE_RE = re.compile(".*(\d{4}).*(\d{2})")
MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))


def date_range_from_title(title):
    # blah blah 2014-15
    m = DATE_RANGE_RE.match(title)
    if not m:
        return "", ""

    yearstart = m.groups()[0]
    yearend = int("{}{}".format(yearstart[0:2], m.groups()[1]))
    yearstart = int(yearstart)
    _, mend = calendar.monthrange(yearend, 3)

    s = "{}-04-01".format( yearstart)
    e = "{}-03-{}".format( yearend, mend)

    return s, e


def process_timeseries(page):
    dataset = {}

    div = page.cssselect('.center')[0]
    dataset['title'] = u"{} - Time Series".format(div.cssselect('h1')[0].text_content())
    dataset['notes'] = page.cssselect('p')[0].text_content()
    dataset['tags'] = ['ambulance', 'timeseries']
    dataset['origin'] = ROOT
    dataset['name'] = slugify.slugify(dataset['title']).lower()

    links = [a for a in div.cssselect('a')]

    resources = []
    for l in links:
        href = l.get('href')
        # Only pull content uploaded here or on dh.gov.uk
        if 'statistics/wp-content' in href\
                or ('dh.gov.uk' in href and not 'webarchive' in href):
            resources.append(anchor_to_resource(l))

    dataset['resources'] = resources

    return [dataset]

def process_single_indicator(anchor):
    dataset = {}

    html = requests.get(anchor.get('href')).content
    page = fromstring(html)
    div = page.cssselect('.center')[0]

    dataset['title'] = div.cssselect('h1')[0].text_content().encode('utf8')
    dataset['tags'] = ['ambulance']
    dataset['origin'] = anchor.get('href')
    dataset['name'] = slugify.slugify(dataset['title']).lower()

    s, e = date_range_from_title(dataset['title'])
    dataset['coverage_start_date'] = s
    dataset['coverage_end_date'] = e


    # The notes/description are from h1 to the first <p><strong>....
    desc = []
    start = page.cssselect('p')[0]
    desc.append(tostring(start))

    stop = False
    while not stop:
        start = start.getnext()
        if len(start.cssselect('strong')) > 0:
            stop = True
            break
        desc.append(tostring(start))

    dataset['notes'] = to_markdown(''.join(desc).encode('utf8'))
    dataset['resources'] = []

    def name_replacement(r):
        r['name'] = r['name'].replace('AmbCO', 'Clinical_Outcomes')
        if 'Indicators' in r['name']:
            r['name'] = r['name'].replace('AmbSYS', 'System')
        else:
            r['name'] = r['name'].replace('AmbSYS', 'System_Indicators')

    links = div.cssselect('p a')
    for link in links:
        href = link.get('href')
        if '/statistics/ambulance-quality-indicators/' in href:
            continue
        if '/statistical-work-areas/ambulance-quality-indicators/' in href:
            continue
        if '#Unifypolicy' in href:
            continue
        r = anchor_to_resource(link, post_create_func=name_replacement)
        dataset['resources'].append(r)

    return dataset

def process_indicators(page):
    datasets = []

    div = page.cssselect('.center')[0]
    links = [a for a in div.cssselect('a') if '/statistics/ambulance-quality-indicators/' in a.get('href')]

    datasets.extend([process_single_indicator(d) for d in links])

    return datasets

def scrape(workspace):
    print "Scraping AQI with workspace {}".format(workspace)

    datasets = []

    html = requests.get(ROOT).content
    page = fromstring(html)

    datasets.extend(process_timeseries(page))
    datasets.extend(process_indicators(page))

    datasets = filter(lambda x: x is not None, datasets)
    print "Found {} datasets".format(len(datasets))
    return datasets