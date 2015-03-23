""" Scraper for http://www.england.nhs.uk/statistics/statistical-work-areas/delayed-transfers-of-care/ """

import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, hd, tl


ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/delayed-transfers-of-care/"
DEFAULT_NOTES = None
YEAR_MATCH = re.compile(".*(\d{4}).*")

def default_notes(page):
    """ Some pages don't have a description.  If we have no DEFAULT_NOTES then
        see if we can find them on the current page for the use in later pages """
    global DEFAULT_NOTES
    if DEFAULT_NOTES:
        return

    print "Getting default notes"
    p = hd([h for h in page.cssselect('h3') if h.text_content().strip() == 'Background'])
    if p is None:
        return

    desc = []
    while True:
        p = p.getnext()
        if p.tag not in ['p', 'ul']:
            break
        s = tostring(p)
        s = s.replace('&', '&amp;')
        desc.append(s)
    DEFAULT_NOTES = to_markdown("".join(desc))


def get_time_series(h3, url):
    print "Time series..."

    dataset = {
        "title": "Delayed Transfers of Care - Time Series",
        "resources": [anchor_to_resource(l) for l in h3.getnext().cssselect('a')],
        "notes": DEFAULT_NOTES,
        "origin": url,
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    return dataset

def add_year_block(header, url):
    m = re.match("(.*)(\d{4})", header.text_content().strip())
    h3 = header

    if h3.getnext() is None:
        # Sometimes the header is hidden in a div. Sigh.
        h3 = h3.getparent()

    links = []
    while h3 is not None:
        h3 = h3.getnext()
        if h3 is None or h3.tag != "p":
            break
        links.extend(h3.cssselect('a'))

    year = m.groups()[1]
    import string
    month = filter(lambda x: x in string.printable, m.groups()[0].strip())

    dataset = {
        "title": u"Delayed Transfers of Care - {} {}".format(month, year),
        "resources": [anchor_to_resource(l) for l in links],
        "notes": DEFAULT_NOTES,
        "origin": url,
        "frequency": "Monthly",
        "groups": ['delayed_transfer']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    mnth = list(calendar.month_name).index(month)
    _, e = calendar.monthrange(int(m.groups()[1]), mnth )
    dataset['coverage_start_date'] = "{}-{}-01".format(m.groups()[1].strip(), mnth)
    dataset['coverage_end_date'] = "{}-{}-{}".format(m.groups()[1].strip(), mnth, e)

    return dataset

def add_singles(page, url):
    links = page.cssselect('.center p a')

    dataset = {
        "title": page.cssselect('h1')[1].text_content().strip(),
        "resources": [],
        "notes": DEFAULT_NOTES,
        "frequency": "Monthly",
        "origin": url,
        "groups": ['delayed_transfer']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    for link in links:
        if not 'Monthly' in link.text_content().strip():
            continue
        dataset["resources"].append(anchor_to_resource(link))

    return dataset

def scrape_page(url):
    html = requests.get(url)
    page = fromstring(html.content)

    print "Scraping", url

    headers = page.cssselect('h3')
    if headers is None:
        headers = page.cssselect('h2')

    datasets = []
    if not headers:
        datasets.append(add_singles(page, url))
    else:
        for h3 in headers:
            s = h3.text_content().strip()
            if "Time Series" in s:
                datasets.append(get_time_series(h3, url))
                continue
            m = YEAR_MATCH.match(s)
            if m:
                print "Processing ", h3.text_content().strip()
                try:
                    datasets.append(add_year_block(h3, url))
                except Exception, e:
                    import traceback
                    print traceback.format_exc()
                    raise

    print "Returning", len(datasets)
    return datasets


def scrape(workspace):
    print "Scraping Delayed Transfer {}".format(workspace)
    global DEFAULT_NOTES

    html = requests.get(ROOT)
    page = fromstring(html.content)
    default_notes(page)

    h3 = hd([h for h in page.cssselect('h3') if h.text_content().strip() == 'Data'])
    links = h3.getnext().cssselect('a')

    datasets = []
    datasets.extend(scrape_page(links[-1].get("href")))
    for l in links:
        datasets.extend(scrape_page(l.get("href")))

    # Get the annual statistical reports
    h3 = hd([h for h in page.cssselect('h3') if h.text_content().strip() == 'Annual Statistical Report'])
    links = h3.getnext().cssselect('a')
    dataset = {
        "resources": [anchor_to_resource(l) for l in links],
        "title": "Delayed Transfers of Care - Annual Statistical Reports",
        "origin": ROOT,
        "notes": DEFAULT_NOTES,
        "frequency": "Annually",
        "groups": ['delayed_transfer']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    datasets.append(dataset)

    datasets = filter(lambda x: x is not None, datasets)
    print "Processed {} datasets".format(len(datasets))
    return datasets

