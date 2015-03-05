import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/winter-daily-sitreps/"

def is_header(p):
    return p.tag == 'p' and len(p.cssselect('strong')) > 0

def scrape_page(url):
    page = fromstring(requests.get(url).content)

    links = [a for a in page.cssselect('a') if ('upload' in a.get('href')) or ('files' in a.get('href'))]
    h1 = page.cssselect('h1')[1]
    desc = []
    p = h1.getparent().getnext()
    while True:
        if is_header(p):
            break
        desc.append(tostring(p))
        p = p.getnext()

    m = re.match(".*(\d{4}).*", h1.text_content().strip())
    year = int(m.groups()[0])

    dataset = {
        "title": h1.text_content().strip(),
        "tags": ["winter", "sitrep"],
        "resources": [anchor_to_resource(a) for a in links],
        "notes": to_markdown("".join(desc)),
        "origin": url,
        "coverage_start_date": "{}-11-01".format(year),
        "coverage_end_date": "{}-03-01".format(year+1),
    }

    return dataset

def scrape(workspace):
    print "Scraping Winter Sit-Reps with workspace {}".format(workspace)
    datasets = []
    page = fromstring(requests.get(ROOT).content)

    pages = [a.get('href') for a in page.cssselect('.center a') if a.text_content().strip().startswith("Winter")]
    for newpage in pages:
        datasets.append(scrape_page(newpage))

    for dataset in datasets:
        dataset["name"] = slugify.slugify(dataset["title"]).lower()

    return datasets
