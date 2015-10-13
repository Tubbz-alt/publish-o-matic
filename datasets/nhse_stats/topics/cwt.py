"""
Scrapes the cancer wait times at
http://www.england.nhs.uk/statistics/statistical-work-areas/cancer-waiting-times/
and
http://www.england.nhs.uk/statistics/category/statistics/commissioner-waiting-cancer/
"""
import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, hd
from publish.lib.encoding import fix_bad_unicode

MONTH_DATE_RANGE_RE = re.compile(".*,\s(.*)\sto\s(.*)\s(\d{4}).*")
DATE_RANGE_RE = re.compile(".*Q(\d)\s(\d{4}).*(\d{2})")
MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))

def anchor_to_resource(resource):
    href = resource.get('href')
    return {
        "description": resource.text_content().encode('utf8'),
        "name": href.split('/')[-1],
        "url": href,
        "format": href[href.rfind(".")+1:].upper(),
    }

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

def scrape_commissioner_page(link):
    # One of these links is not like the others....
    # if link.get('href') == 'http://www.england.nhs.uk/statistics/2012/03/23/cwt-april-to-december-2011/':
    #     # Special case....
    #     return None


    # Find all the li a underneath the .column.center
    html = requests.get(link)
    dom = fromstring(html.content)

    div = dom.cssselect('.column.center')[0]    
    title = div.cssselect('h1')[0].text_content().strip()


    links = div.cssselect('li a')
    if len(links) == 0:
        links = div.cssselect('a')

    resources = [anchor_to_resource(link) for link in links]
    resources = [r for r in resources if len(r['format']) <= 4 ]

    dataset = {}

    drs, dre = date_range_from_title(title)

    dataset['title'] = title
    dataset['name'] = slugify.slugify(title).lower()
    if len(div.cssselect('article p')) > 0:
        dataset["notes"] = to_markdown( fix_bad_unicode(unicode(tostring(div.cssselect('article p')[0]))) )
    dataset["tags"] = ["CWT"]
    dataset["resources"] = resources
    dataset["origin"] = link.get('href')
    dataset["groups"] = ['cwt']
    if drs:
        dataset["coverage_start_date"] = drs
    if dre:
        dataset["coverage_end_date"] = dre
    dataset["frequency"] = "Quarterly"

    return dataset


def multipage_fetch(root):
    datasets = []
    fourohfour = False
    page = 1
    links = []

    while not fourohfour:
        html = requests.get(root.format(page))
        fourohfour = html.status_code == 404
        if fourohfour:
            break

        page = page + 1
        dom = fromstring(html.content)

        links.extend(dom.cssselect('h2 a'))

    for link in links:
        datasets.append(scrape_commissioner_page(link))

    return datasets

def commissioner_based():
    return multipage_fetch("http://www.england.nhs.uk/statistics/category/statistics/commissioner-waiting-cancer/page/{}/")

def default_cwt():
    return multipage_fetch("http://www.england.nhs.uk/statistics/category/statistics/provider-waiting-cancer/page/{}/")


def scrape(workspace):
    print "Scraping CWT with workspace {}".format(workspace)

    datasets = []
    bases = [
        'http://www.england.nhs.uk/statistics/statistical-work-areas/cancer-waiting-times/provider-based-cancer-waiting-times-statistics/',
        'http://www.england.nhs.uk/statistics/statistical-work-areas/cancer-waiting-times/commissioner-based-cancer-waiting-times-statistics/'
    ]
    targets = []
    for base in bases: 
        html = requests.get(base)
        page = fromstring(html.content)
        
        h3 = hd([h for h in page.cssselect('h3') if h.text_content().strip().lower() == 'latest statistics'])
        links = [a.get('href') for a in h3.getnext().cssselect('a')]
        for l in links:
            print l
        targets += links
        
    for t in targets:
        datasets.append(scrape_commissioner_page(t))
    # datasets.extend(commissioner_based())
    # datasets.extend(default_cwt())



    datasets = filter(lambda x: x is not None, datasets)
    return datasets
