"""
Scrapes the friends and family test data at
http://www.england.nhs.uk/statistics/statistical-work-areas/friends-and-family-test/friends-and-family-test-data/
"""
import calendar
import datetime
import re


from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown


TITLE_ROOT = "Friends and Family Test"
ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/friends-and-family-test/friends-and-family-test-data/"

YEARS_RE = re.compile("(\d{4}-\d{2})")
DATE_RE = re.compile(".*\s(.*)\s(\d{4})")
MONTHS_LOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))

def anchor_to_resource(resource):
    href = resource.get('href')
    return {
        "description": resource.text_content().encode('utf8'),
        "name": href.split('/')[-1],
        "url": href,
        "format": href[href.rfind(".")+1:].upper(),
    }

def process_block(p, title, description, current_year):
    if not current_year:
        return None

    dataset = {
        "title": "{} - {} - {}".format(TITLE_ROOT, title, current_year),
        "notes": description,
        "tags": ["Friends and Family", "Statistics", current_year, title.replace('&',' and ')],
        "resources": [],
        "source": "http://www.england.nhs.uk/statistics/statistical-work-areas/friends-and-family-test"
    }

    for resource in p.cssselect('a'):
        dataset["resources"].append(anchor_to_resource(resource))

    dataset["name"] = slugify.slugify(dataset['title']).lower()

    return dataset

def contains_year(element):
    m = YEARS_RE.match(element.text_content().strip())
    if m:
        return m.groups()[0]
    return None

def process_latest(datasets, latest):
    """
    We process the latest data as a special case because it is
    all munged together in a separate block.  We need to find the
    links, parse them, try and group them by name, and then decide
    how we're going to label the dataset.
    """
    for anchor in latest:
        resource = anchor_to_resource(anchor)
        finder = resource['description'].split(' ')[1]

        finder = "{} - {} -".format(TITLE_ROOT, finder)

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
    return d.isoformat()

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
    print "Scraping FAF with workspace {}".format(workspace)

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

    # Process the individual datasets
    current_label = ""
    generator = (p for p in paras[num_p:])
    for p in generator:
        strong = p.cssselect('STRONG')
        if len(strong) > 0:
            # If this strong element is a year range, we should remember it
            c = contains_year(strong[0])
            if c:
                current_year = c
                #print "Current_year is now", current_year
                continue

            current_label = strong[0].text_content().strip()
            if len(p.cssselect('a')) == 0:
                # Some blank paras on the page, and some where the title is separate
                # from the links.  In this case, just skip to the next para
                p = generator.next()
            datasets.append(process_block(p, current_label, description, current_year))


    # Find and process the latest datasets ...
    latest_data = []
    process_links = False
    for p in paras:
        strong = p.cssselect('STRONG')
        if len(strong) == 1:
            if strong[0].text_content().strip() == "Latest Data":
                process_links = True
            else:
                process_links = False
                continue

        if process_links:
            latest_data.extend(p.cssselect('a'))

    datasets = filter(lambda x: x is not None, datasets)
    process_latest(datasets, latest_data)
    process_dates(datasets)

    return datasets
