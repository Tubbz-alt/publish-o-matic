""" Diagnotic Census Data from http://www.england.nhs.uk/statistics/statistical-work-areas/diagnostics-waiting-times-and-activity/diagnostics-census-data/ """
import collections
import calendar
import datetime
import re
import urllib

from lxml.html import fromstring, tostring
import requests
import slugify

from publish.lib.helpers import to_markdown, anchor_to_resource, get_dom

OVERNIGHT = "http://www.england.nhs.uk/statistics/statistical-work-areas/bed-availability-and-occupancy/bed-data-overnight/"
DAYONLY = "http://www.england.nhs.uk/statistics/statistical-work-areas/bed-availability-and-occupancy/bed-data-day-only/"
RESIDENTIAL = "http://webarchive.nationalarchives.gov.uk/20130107105354/http://www.dh.gov.uk/en/Publicationsandstatistics/Statistics/Performancedataandstatistics/Beds/DH_077450"
CRITICAL_CARE = "http://webarchive.nationalarchives.gov.uk/20130107105354/http://www.dh.gov.uk/en/Publicationsandstatistics/Statistics/Performancedataandstatistics/Beds/DH_077451"


YR_MATCH = re.compile('.*(\d{4}).*')

def historical_beds(page, url, title):
    dataset = {}

    desc = page.cssselect('.introText')[0].text_content().strip().encode('utf8')

    sublinks = sorted(page.cssselect('.subLinks a'), key=lambda x: x.text_content().strip())
    print len(sublinks)
    first = int(re.match(".*(\d{4}).*", sublinks[0].text_content()).groups()[0])
    last = int(re.match(".*(\d{4}).*", sublinks[-1].text_content()).groups()[0]) + 1

    dataset["title"] = title
    dataset["origin"] = url
    dataset["coverage_start_date"] = "{}-04-01".format(first)
    dataset["coverage_end_date"] = "{}-03-31".format(last)
    dataset["name"] = slugify.slugify(title).lower()
    dataset["resources"] = [anchor_to_resource(a) for a in sublinks]
    dataset["notes"] = desc

    return dataset

def current_beds(page, url, title):
    datasets = []

    div = page.cssselect('.center')[0]
    desc = div.cssselect('p')[0].text_content().strip()

    all_resources = [anchor_to_resource(a) for a in div.cssselect('p a') if 'XLS' in a.text_content()]
    grouped = collections.defaultdict(list)

    for resource in all_resources:
        if "Time" in resource['description']:
            grouped['TimeSeries'].append(resource)
            continue

        yr = YR_MATCH.match(resource['description']).groups()[0]
        grouped[yr].append(resource)

    for y in sorted(grouped.keys()):
        dataset = {}
        if y == 'TimeSeries':
            dataset["title"] = "{} - Timeseries".format(title)
        else:
            dataset["title"] = "{} {}-{}".format(title, y, int(y)+1)
            dataset["coverage_start_date"] = "{}-04-01".format(y)
            dataset["coverage_end_date"] = "{}-03-31".format(int(y)+1)

        dataset["name"] = slugify.slugify(dataset["title"]).lower()
        dataset["origin"] = url
        dataset["tags"] = ["bed availability"]
        dataset["notes"] = desc
        dataset["resources"] = grouped[y]
        datasets.append(dataset)


    return datasets


def scrape(workspace):
    print "Scraping Bed Availability with workspace {}".format(workspace)
    datasets = []

    dom = get_dom(OVERNIGHT)
    datasets.extend(current_beds(dom, OVERNIGHT, "Bed Availability and Occupancy Data - Overnight"))

    dom = get_dom(DAYONLY)
    datasets.extend(current_beds(dom, DAYONLY, "Bed Availability and Occupancy Data - Day Only"))

    dom = get_dom(RESIDENTIAL)
    datasets.append(historical_beds(dom, RESIDENTIAL, "Residential Care Beds Availability"))

    dom = get_dom(CRITICAL_CARE)
    datasets.append(historical_beds(dom, CRITICAL_CARE, "Critical Care Beds Availability"))

    print datasets[-1]
    datasets = filter(lambda x: x is not None, datasets)
    print len(datasets)
    return datasets
