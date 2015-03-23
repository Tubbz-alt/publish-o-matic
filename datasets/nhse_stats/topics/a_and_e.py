"""
Scrapes the A and E waiting times at
http://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/
"""
import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, hd, tl


ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/"
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
        if p.tag != 'p':
            break
        s = p.text_content().strip()
        s = s.replace('&', '&amp;')
        desc.append(s)
    DEFAULT_NOTES = to_markdown("".join(desc))


def get_time_series(h3, url):
    print "Time series..."

    dataset = {
        "title": "A&E Attendances and Emergency Admissions - Time Series",
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

    from publish.lib.encoding import fix_bad_unicode
    txt = fix_bad_unicode(unicode(header.text_content().strip()))

    dataset = {
        "title": u"A&E Attendances and Emergency Admissions - {}".format(txt),
        "resources": [anchor_to_resource(l) for l in links],
        "notes": DEFAULT_NOTES,
        "origin": url,
        "frequency": "Weekly",
        "groups": ['a_and_e']
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()

    mname = m.groups()[0].strip().encode('ascii', 'ignore')
    mnth = list(calendar.month_name).index(mname)
    _, e = calendar.monthrange(int(m.groups()[1]), mnth )
    dataset['coverage_start_date'] = "{}-{}-01".format(m.groups()[1].strip(), mnth)
    dataset['coverage_end_date'] = "{}-{}-{}".format(m.groups()[1].strip(), mnth, e)

    return dataset

def scrape_page(url):
    html = requests.get(url)
    page = fromstring(html.content)
    default_notes(page)

    print "Scraping", url

    headers = page.cssselect('h3')
    if headers is None:
        headers = page.cssselect('h2')

    datasets = []
    for h3 in headers:
        s = h3.text_content().strip()
        if "Time Series" in s:
            datasets.append(get_time_series(h3, url))
        m = YEAR_MATCH.match(s)
        if m:
            datasets.append(add_year_block(h3, url))

    print "Returning", len(datasets)
    return datasets


def scrape(workspace):
    print "Scraping A&E Waiting Times with workspace {}".format(workspace)

    html = requests.get(ROOT)
    page = fromstring(html.content)

    h3 = hd([h for h in page.cssselect('h3') if h.text_content().strip() == 'Weekly Data and Quarterly Aggregates'])
    links = h3.getnext().cssselect('a')

    datasets = []
    for l in links:
        try:
            datasets.extend(scrape_page(l.get("href")))
        except:
            import traceback
            traceback.print_exc()

    datasets = filter(lambda x: x is not None, datasets)
    print "Processed {} datasets".format(len(datasets))
    return datasets

