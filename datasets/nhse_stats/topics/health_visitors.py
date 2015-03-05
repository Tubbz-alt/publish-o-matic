import collections
import calendar
import datetime
import re

from lxml.html import fromstring, tostring
import requests
import slugify
import string

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom

MONTH_YEAR_MATCHER = re.compile("(.*?)(\d{4}).*")
INDICATIVE_DESC = None

HISTORICAL = "http://www.england.nhs.uk/statistics/statistical-work-areas/health-visitors/indicative-health-visitor-collection-ihvc/historical-data/"
METRICS_URL = "http://www.england.nhs.uk/statistics/statistical-work-areas/health-visitors/health-visitors-service-delivery-metrics/"

def _is_header(element):
    return element.tag == 'p' and len(element.cssselect('strong')) > 0

def make_dataset(txt, description, resources, url):
    text = filter(lambda x: x in string.printable, txt)
    m = MONTH_YEAR_MATCHER.match(text)
    month = m.groups()[0].strip()
    year = int(m.groups()[1])
    month_pos = list(calendar.month_name).index(month)
    _, e = calendar.monthrange(year, month_pos)
    month_pos = str(month_pos).zfill(2)

    dataset = {
        "title": u"Indicative Health Visitor Collection - {} {}".format(month, year),
        "resources": resources,
        "notes": description,
        "origin": url,
        "coverage_start_date": "{}-{}-01".format(year, month_pos),
        "coverage_end_date": "{}-{}-{}".format(year, month_pos, e),
        "tags": ["IHVC"]
    }

    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    return dataset

def historical_indicative():
    page = fromstring(requests.get(HISTORICAL).content)
    datasets = []

    current_resources = None

    paras = page.cssselect('.center p')
    for p in paras:
        text = p.text_content()
        if MONTH_YEAR_MATCHER.match(text) and not 'website' in text:
            current_resources = [anchor_to_resource(a) for a in p.getnext().cssselect('a')]
            if len(current_resources) > 0:
                datasets.append(make_dataset(text, INDICATIVE_DESC, current_resources, HISTORICAL))

    return datasets

def scrape_indicative():
    global INDICATIVE_DESC
    datasets = []
    page = fromstring(
        requests.get("http://www.england.nhs.uk/statistics/statistical-work-areas/health-visitors/indicative-health-visitor-collection-ihvc/").content)


    desc = []
    guidance_resources = []

    headerPs = page.cssselect('p strong')
    for h in headerPs:
        txt = h.text_content().strip().encode('utf8')
        if txt.startswith("Background"):
            p = h.getparent().getnext()
            while not _is_header(p):
                desc.append(tostring(p))
                p = p.getnext()
        elif txt.startswith("Guidance"):
            p = h.getparent().getnext()
            while not _is_header(p):
                for a in p.cssselect('a'):
                    guidance_resources.append(anchor_to_resource(a))
                p = p.getnext()
        elif MONTH_YEAR_MATCHER.match(txt):
            description = to_markdown("\n".join(desc))
            if not INDICATIVE_DESC:
                INDICATIVE_DESC = description

            resources = []
            p = h.getparent().getnext()
            while not _is_header(p):
                for a in p.cssselect('a'):
                    resources.append(anchor_to_resource(a))
                p = p.getnext()
            datasets.append(make_dataset(txt,
                                         description,
                                         resources + guidance_resources,
                                         "http://www.england.nhs.uk/statistics/statistical-work-areas/health-visitors/indicative-health-visitor-collection-ihvc/"))

    return datasets

def scrape_metrics():
    datasets = []
    page = fromstring(requests.get(METRICS_URL).content)

    matcher = re.compile(".*Q(\d{1})\s(\d{4})-(\d{2}).*")

    h1 = page.cssselect('h1')[1].getparent()
    title = h1.text_content().strip()

    desc = []
    while True:
        h1 = h1.getnext()
        if len(h1.cssselect('strong')) > 0:
            break
        desc.append(tostring(h1))
    description = to_markdown("".join(desc))

    links = page.cssselect('p a')
    unsorted_links = collections.defaultdict(list)
    for l in links:
        m = matcher.match(l.text_content())
        if not m:
            continue
        k = "{}-{}".format(m.groups()[1], m.groups()[2])
        unsorted_links[k].append( [l, m.groups()] )


    for k, v in unsorted_links.iteritems():
        dataset = {
            "title": "{} {}".format(title, k),
            "notes": description,
            "origin": METRICS_URL,
            "resources": [],
            "frequency": "Quarterly"
        }
        dataset["name"] = slugify.slugify(dataset["title"]).lower()
        for link, time_tuple in v:
            dataset["resources"].append(anchor_to_resource(link))
        datasets.append(dataset)

    return datasets

def scrape(workspace):
    print "Scraping Health Visitor Data with workspace {}".format(workspace)
    datasets = []

    datasets.extend(scrape_indicative())
    datasets.extend(historical_indicative())
    datasets.extend(scrape_metrics())

    datasets = filter(lambda x: x is not None, datasets)
    return datasets