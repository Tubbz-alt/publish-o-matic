"""
Scrapes the referral to treatment times at
http://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/
"""
import calendar
import datetime
import re

from bs4 import BeautifulSoup

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown


TITLE_ROOT = "Consultant-led Referral to Treatment Waiting Times"
ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/"

DATE_RE = re.compile("(.*)\s(\d{4})")
MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))


def anchor_to_resource(resource):
    href = resource.get('href')
    return {
        "description": resource.text_content().encode('utf8'),
        "name": href.split('/')[-1],
        "url": href,
        "format": href[href.rfind(".")+1:].upper(),
    }

def string_to_date(s, start=True):

    m = DATE_RE.match(s)
    if not m:
        return ""

    if not len(m.groups()) == 2:
        return ""

    mnth = MONTHS_LOOKUP.get(m.groups()[0].strip(), "")
    year = int(m.groups()[1].strip())

    if not mnth:
        return ""

    day = 1
    _, mend = calendar.monthrange(year, mnth)
    if not start:
        day = mend

    d = datetime.datetime(year=year, month=mnth, day=day)
    return d.strftime("%Y-%m-%d")


def create_dataset(title, description, links):
    dataset = {}

    dataset['title'] = "{} - {}".format(TITLE_ROOT, title)
    dataset['name'] = slugify.slugify(dataset['title']).lower()
    dataset["notes"] = description
    dataset["tags"] = ["RTT", "Statistics", string_to_date(title)[0:4]]
    dataset["resources"] = []
    dataset["origin"] = ROOT
    dataset["coverage_start_date"] = string_to_date(title)
    dataset["coverage_end_date"] = string_to_date(title,start=False)
    dataset["frequency"] = "Monthly"
    dataset["groups"] = ["rtt"]
    for resource in links:
        dataset["resources"].append(anchor_to_resource(resource))

    return dataset

def get_description(soup):
    details = soup.find("article").find_all("ul")
    description = []
    for detail in details:
        list_items = [i.get_text() for i in detail.find_all('li')]
        description.extend(list_items)
    return to_markdown("\n".join(description))

def process_link(link):
    datasets = []

    href = link.get('href')
    if not href.startswith('https://www.england.nhs.uk'):
        return [None]

    print "Processing sub-page: {}".format(href)
    html = requests.get(href)
    soup = BeautifulSoup(html.content)
    page = fromstring(html.content)

    # description is from the ul to the first hr.
    description = []
    elem = page.cssselect('.page-content')
    read = False
    hr_count = 0

    description = get_description(soup)

    for h in page.cssselect('h3'):
        # Read all elements from h down to next hr
        paras = []
        next_block = h
        header = next_block.text_content().strip()
        while next_block.tag != 'hr':
            next_block = next_block.getnext().cssselect('p')
            if not next_block:
                break
            next_block = next_block[0]
            paras.extend(next_block.cssselect('a'))

        datasets.append(create_dataset(header, description, paras))

    return datasets

def is_old(dataset):
    end_date = datetime.datetime.strptime(dataset["coverage_end_date"], "%Y-%m-%d").date()
    return end_date < datetime.date(2015, 9, 1)

def scrape(workspace):
    print "Scraping RTT with workspace {}".format(workspace)

    datasets = []

    html = requests.get(ROOT)
    page = fromstring(html.content)

    latest = page.cssselect('h3')[0]
    container = latest.getnext().cssselect('p')[0]
    for link in container.cssselect('a'):
        datasets.extend(process_link(link))

    datasets = filter(lambda x: x is not None, datasets)

    datasets = [i for i in datasets if not is_old(i)]


    # Create a dataset per year from the datasets we were given.
    return datasets
