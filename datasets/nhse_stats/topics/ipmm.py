import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/integrated-performance-measures-monitoring/"

YEAR_MATCHER = re.compile("(\d{4})-(\d{2})")

def scrape_archived_page(page, url):
    title = "IPMM - {}".format(page.cssselect('.introContent h2')[0].text_content().strip())
    description = page.cssselect('.introText')[0].text_content().strip()

    dataset = {
        "title": title,
        "notes": description,
        "resources": [anchor_to_resource(a) for a in page.cssselect('.internalLink') if a.text_content().strip().startswith('Download')],
        "origin": url,
    }
    return [dataset]

def scrape_page(url):
    page = fromstring(requests.get(url).content)
    if 'webarchive' in url:
        return scrape_archived_page(page, url)

    datasets = []

    h = page.cssselect('h1')[1]
    title = "IPMM - {}".format(h.text_content().strip())

    desc = []
    p = h.getparent().getnext()
    while True:
        if not p.tag == 'p' or len(p.cssselect('a')) > 0:
            break
        desc.append(tostring(p))
        p = p.getnext()
    description = to_markdown("".join(desc))

    hs = page.cssselect('.center h4')
    if len(hs) < 2:
        hs = page.cssselect('.center h3')

    for h in hs:
        subtitle = "{} - {}".format(title, h.text_content().strip())
        links = h.getnext().cssselect('a')

        m = YEAR_MATCHER.match(h.text_content().strip())
        year_start = int(m.groups()[0])

        dataset = {
            "title": subtitle,
            "notes": description,
            "origin": url,
            "resources": [anchor_to_resource(a) for a in links],
            "coverage_start_date": "{}-04-01".format(year_start),
            "coverage_end_date": "{}-03-31".format(year_start+1),
            "frequency": "Annually",
            "groups": ['ipmm']
        }
        datasets.append(dataset)

    return datasets

def scrape(workspace):
    print "Scraping IPMM with workspace {}".format(workspace)
    datasets = []

    page = fromstring(requests.get(ROOT).content)
    page_list = page.cssselect('.center ul')[1].cssselect('a')
    for p in page_list:
        datasets.extend(scrape_page(p.get('href')))


    datasets = filter(lambda x: x is not None, datasets)
    for dataset in datasets:
        dataset["tags"] = ["ipmm"]
        dataset["name"] = slugify.slugify(dataset["title"]).lower()
    print len(datasets)
    return datasets
