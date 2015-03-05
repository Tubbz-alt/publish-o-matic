import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom, hd

MONTHLY = "http://www.england.nhs.uk/statistics/statistical-work-areas/hospital-activity/monthly-hospital-activity/mar-data/"
QUARTERLY = "http://www.england.nhs.uk/statistics/statistical-work-areas/hospital-activity/quarterly-hospital-activity/qar-data/"

YEAR_MATCHER = re.compile("(\d{4})-(\d{2})")

def process_monthly(page):
    datasets = []

    title = "Monthly Hospital Activity Data"
    description = "Monthly activity data relating to elective and non-elective inpatient "\
                  "admissions (FFCEs) and outpatient referrals and attendances for first "\
                  "consultant outpatient appointments."

    headers = page.cssselect('h3,h4')
    for h in headers:
        text = h.text_content().strip()

        if re.match("(\d{4})-(\d{2})", text):
            datasets.extend(process_block(h, _p_strong("Provider based"),
                                          _p_strong("Commissioner based"),title, description,QUARTERLY))

    provider_links, commissioner_links = [], []
    h3prev = hd([h for h in page.cssselect('h3') if h.text_content().strip().startswith("Previous")])
    p = h3prev.getnext()
    while True:
        if len(p) == 0:
            break
        if _p_strong("Provider based")(p):
            provider_links = p.getnext().cssselect('a')
        if _p_strong("Commissioner based")(p):
            commissioner_links = p.getnext().cssselect('a')

        p = p.getnext()

    for l in provider_links:
        m = re.match(".*(\d{4})-\d{2}.*", l.text_content().encode('utf8'))
        yr = int(m.groups()[0])
        csd = "{}-04-01".format(yr)
        ced = "{}-03-31".format(yr+1)
        pdataset = {
            "title": "{} - Provider based - {}-{}".format(title, yr, yr+1),
            "notes": description,
            "origin": MONTHLY,
            "resources": [anchor_to_resource(l)],
            "frequency": "Annual",
            "coverage_start_date": csd,
            "coverage_end_date": ced,
        }
        pdataset["name"] = slugify.slugify(pdataset["title"]).lower()
        datasets.append(pdataset)

    for l in commissioner_links:
        m = re.match(".*(\d{4})-\d{2}.*", l.text_content().encode('utf8'))
        yr = int(m.groups()[0])
        csd = "{}-04-01".format(yr)
        ced = "{}-03-31".format(yr+1)
        cdataset = {
            "title": "{} - Provider based - {}-{}".format(title, yr, yr+1),
            "notes": description,
            "origin": MONTHLY,
            "resources": [anchor_to_resource(l)],
            "frequency": "Annual",
            "coverage_start_date": csd,
            "coverage_end_date": ced,
        }
        cdataset["name"] = slugify.slugify(cdataset["title"]).lower()
        datasets.append(cdataset)


    time_series_links = [a for a in page.cssselect('a') if 'Timeseries' in a.get('href')]
    dataset = {
        "title": "{} - Time Series".format(title),
        "notes": description,
        "origin": MONTHLY,
        "resources": [anchor_to_resource(a) for a in time_series_links]
    }
    dataset["name"] = slugify.slugify(dataset["title"]).lower()
    datasets.append(dataset)

    return datasets

def process_block(block, provider_fn, commissioner_fn, title, desc, origin):
    # Continue cycling until we provider_fn matches an element
    # then getnext().cssselect('a'), same for commissioner_fn
    p = block.getnext()

    provider_links = []
    commissioner_links = []

    print block.text_content().strip()
    while True:
        if provider_fn(p):
            provider_links = p.getnext().cssselect('a')
        if commissioner_fn(p):
            commissioner_links = p.getnext().cssselect('a')
        if p.tag != 'p':
            break

        p = p.getnext()

    csd, ced = "", ""
    m = YEAR_MATCHER.match(block.text_content().strip())
    if m:
        syear = int(m.groups()[0])
        eyear = syear + 1
        csd = "{}-04-01".format(syear)
        ced = "{}-03-31".format(eyear)

    pdataset = {
        "title": "{} - Provider based - {}".format(title, block.text_content().strip()),
        "resources": [anchor_to_resource(a) for a in provider_links],
        "origin": origin,
        "notes": desc,
        "coverage_start_date": csd,
        "coverage_end_date": ced,
    }
    pdataset["name"] = slugify.slugify(pdataset["title"]).lower()

    cdataset = {
        "title": "{} - Commissioner based - {}".format(title, block.text_content().strip()),
        "resources": [anchor_to_resource(a) for a in commissioner_links],
        "origin": origin,
        "notes": desc,
        "coverage_start_date": csd,
        "coverage_end_date": ced,
    }
    cdataset["name"] = slugify.slugify(cdataset["title"]).lower()

    return [pdataset, cdataset]

def _p_strong(nm):
    def _inner(p):
        strong = p.cssselect('strong')
        if len(strong) == 0:
            return False
        return strong[0].text_content().strip() == nm
    return _inner

def process_quarterly(page):
    datasets = []

    title = "Quarterly Hospital Activity Data"
    description = "Quarterly activity data relating to GP and other referrals for "\
                  "an outpatient appointment, the total number of attendances at "\
                  "consultant outpatient clinics; including patients seen for their "\
                  "first appointments as well as those attending for subsequent or follow "\
                  "up appointments. Also, the number of patients who did not attend their "\
                  "outpatient appointment and gave no advance warning or those who arrived "\
                  "too late to be seen. Elective admission events are decisions to admit, "\
                  "patients admitted, patients failed to attend, removals other than admission, "\
                  "patients suspended and patients who have self-deferred. Figures are "\
                  "submitted quarterly on the Quarterly Activity Return (QAR) by NHS Trusts "\
                  "and Independent sector providers treating NHS patients."

    headers = page.cssselect('h3,h4')
    for h in headers:
        text = h.text_content().strip()
        if text == "Time Series":
            datasets.extend(process_block(h, _p_strong("Provider based"),
                                          _p_strong("Commissioner based"),title, description, QUARTERLY))
        elif re.match("(\d{4})-(\d{2})", text):
            datasets.extend(process_block(h, _p_strong("Provider based"),
                                          _p_strong("Commissioner based"),title, description,QUARTERLY))


    return datasets

def scrape(workspace):
    print "Scraping Hospital Activity with workspace {}".format(workspace)
    datasets = []

    monthly_page = fromstring(requests.get(MONTHLY).content)
    datasets.extend(process_monthly(monthly_page))

    quarterly_page = fromstring(requests.get(QUARTERLY).content)
    datasets.extend(process_quarterly(quarterly_page))

    datasets = filter(lambda x: x is not None, datasets)
    for dataset in datasets:
        dataset["tags"] = ["hospital activity", "provider based", "commissioner based"]
    print len(datasets)
    return datasets
