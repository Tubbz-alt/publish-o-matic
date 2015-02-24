""" Scrapes the data at http://www.england.nhs.uk/statistics/statistical-work-areas/mixed-sex-accommodation/msa-data/ """

import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource


TITLE_ROOT = "Mixed-Sex Accommodation Data"
ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/mixed-sex-accommodation/msa-data/"

DATE_RE = re.compile(".*\s(.*)\s(\d{4})")
MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))


def process_block(p, title, description, current_year):
    if not current_year:
        return None

    dataset = {
        "title": "{} - {}".format(TITLE_ROOT, title),
        "notes": description,
        "tags": ["Statistics", current_year],
        "resources": [],
        "origin": "http://www.england.nhs.uk/statistics/statistical-work-areas/mixed-sex-accommodation/msa-data/"
    }

    for resource in p.cssselect('a'):
        r = anchor_to_resource(resource)
        if r['format'] == 'XLSM':
            r['format'] = 'XLS'
        dataset["resources"].append(r)

    dataset["name"] = slugify.slugify(dataset['title']).lower()

    return dataset

def process_latest(datasets, latest):
    """
    We process the latest data as a special case because it is
    all munged together in a separate block.  We need to find the
    links, parse them, try and group them by name, and then decide
    how we're going to label the dataset.
    """
    for anchor in latest:
        resource = anchor_to_resource(anchor)
        y = int(string_to_date(resource['description'])[:4])
        finder = "{}-{}".format(y-1, str(y)[2:4])
        finder = "{} - {}".format(TITLE_ROOT, finder)

        # We can find the first dataset in the list (datasets) whose
        # title starts with finder as the most recent years go at
        # the top of the list on the page.
        for dataset in datasets:
            if dataset['title'].startswith(finder):
                print "We think ", resource['description'], "goes in", dataset['title']
                dataset['resources'].insert(0, resource)
                break

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

def process_dates(datasets):

    for dataset in datasets:
        start_date = string_to_date(dataset["resources"][-1]['description'])
        end_date = string_to_date(dataset["resources"][0]['description'], start=False)
        dataset["coverage_start_date"] = start_date
        dataset["coverage_end_date"] = end_date
        dataset["frequency"] = "Monthly"

        qrtrs = [1 for r in dataset['resources'] if 'Quarter' in r['description']]
        if any(qrtrs):
            dataset["frequency"] = "Quarterly"

def scrape(workspace):
    print "Scraping MSA with workspace {}".format(workspace)

    datasets = []

    page = requests.get(ROOT)
    html = fromstring(page.content)

    center = html.cssselect('.column.center')[0]

    paras = list(center.cssselect('P'))

    current_year = None

    # Iterate through all of the Ps. From here until we find a <strong>
    # is the description
    description = []
    num_p = 0
    for p in paras:
        if len(p.cssselect('STRONG')) > 0:
            break
        num_p += 1
        description.append(tostring(p))
    description = to_markdown(''.join(description))

    latest_data_links = []

    # Process the individual datasets
    current_label = ""
    generator = (p for p in paras[num_p:])
    for p in generator:
        strong = p.cssselect('STRONG')
        if len(strong) > 0:
            current_label = strong[0].text_content().strip()
        else:
            if current_label == 'Latest Data':
                latest_data_links = p.cssselect('a')
                continue

            datasets.append(process_block(p, current_label, description, current_label))

    datasets = filter(lambda x: x is not None, datasets)
    process_dates(datasets)
    process_latest(datasets, latest_data_links)

    print len(datasets)
    return datasets
