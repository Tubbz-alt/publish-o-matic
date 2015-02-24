"""
Scraper for the patient survey website at https://gp-patient.co.uk/surveys-and-reports
"""
from itertools import cycle
import json
import re
from urllib import unquote

import ffs
import requests
import slugify
from lxml.html import fromstring, tostring

from publish.lib.helpers import anchor_to_resource, to_markdown

DESCRIPTIONS = {
    'Practice': "Practice Level Report",
    'PCT Level': "PCT Level Report",
    'Summary Report': 'Summary Report',
    'National Level': 'National Level',
    'National Comment': 'National Commentary Report',
    'List of': 'List of report variables',
    'Care Planning': 'Care Planning Report',
    'Dentistry': 'Dentistry Report',
    'Out of Hours': 'Out of Hours Report',
    'CCG Report': 'CCG Report',
    'CCG Level': 'CCG Level Report',
    'CCG Data': 'CCG Data',
    'AT Report': 'Area Team Report'
}

def description_for_link(link, resource):
    u = unquote(link.get('href'))

    desc = ""
    for k, v in DESCRIPTIONS.iteritems():
        if k in u:
            desc = v
            break

    if not desc:
        if resource['description'] in ['Excel', 'CSV']:
            # Try and determine description from surrounding link
            s =  link.getparent().text_content().strip().encode("utf8")
            desc = "{} ({})".format(s[0:s.index('(')].strip(), resource['description'])
        return desc

    ext = u.split('.')[-1].upper()
    desc = "{} ({})".format(desc, ext)

    return desc

def process_div(title, h2):
    div = h2.getparent()

    resources = []

    weighting_table = None

    for table in div.cssselect('table'):
        c = cycle([th.text_content() for th in table.cssselect('thead tr th')])
        cells = [td.cssselect('a') for td in table.cssselect('tbody tr td')]
        for cell in cells:
            header = c.next()
            if not '-' in header:
                weighting_table = table
                continue

            txt = cell[0].text_content()
            if len(txt) == 1:
                txt = "Questionnaire {}".format(txt)

            r = anchor_to_resource(cell[0].cssselect('a')[0],
                title="{} - {}".format(txt, header))
            r['name'] = unquote(r['name'])
            resources.append(r)

            if len(cell) == 2:
                txt = cell[1].text_content()
                if len(txt) == 1:
                    txt = "Questionnaire {}".format(txt)
                r = anchor_to_resource(cell[1].cssselect('a')[0],
                    title="{} - {}".format(txt, header))
                r['name'] = unquote(r['name'])
                resources.append(r)

    if weighting_table is None:
        weighting_table = div.getparent().getnext().cssselect('table')[0]

    notes = "The GP Patient Survey is an independent survey run by Ipsos MORI on behalf of "\
        "NHS England.  The survey is sent out to over a million people across the UK. "\
        "The results show how people feel about their GP practice. The data below is for {}".format(title)


    year = re.match('.*(\d{4})', title).groups()[0]

    dataset = {
        "title": "GP Survey Data - {}".format(title),
        "tags": ["gp survey", "NHSOF"],
        "resources": [],
        "coverage_start_date": "{}-01-01".format(year),
        "coverage_end_date": "{}-12-31".format(year),
        "notes": notes,
        "origin": "https://gp-patient.co.uk/surveys-and-reports",
    }
    dataset["name"] = slugify.slugify(dataset['title']).lower()

    links = weighting_table.cssselect('a')
    links = [link for link in links if link.get('href') != '#']
    for l in links:
        r = anchor_to_resource(l)
        r['name'] = unquote(r['name'])
        d = description_for_link(l, r)
        r['description'] = d or r['description']
        dataset['resources'].append(r)

    return dataset


def main(workspace):
    datasets = []
    folder = ffs.Path(workspace) / 'data'
    folder.mkdir()

    html = requests.get("https://gp-patient.co.uk/surveys-and-reports").content
    page = fromstring(html)

    divs = page.cssselect('div h2')[1:]
    for h2 in divs:
        title = h2.text_content().strip()
        if title.startswith('Latest'):
            title = title.replace('Latest survey and reports', '').strip()
        datasets.append(process_div(title, h2))


    json.dump(datasets, open(folder / 'metadata.json', 'w'))
