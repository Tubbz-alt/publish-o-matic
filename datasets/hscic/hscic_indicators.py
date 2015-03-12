# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Grabs all the indicators published by HSCIC.

Each indicator has a unique ID. Currently (October 2014) the upper limit is
1698. Each indicator can be obtained with the following URL (remembering to
replace the integer value at the end):


https://indicators.ic.nhs.uk/webview/velocity?v=2&mode=documentation&submode=ddi&study=http%3A%2F%2F172.16.9.26%3A80%2Fobj%2FfStudy%2FP01698
"""
import os
import json
import logging
import requests
from bs4 import BeautifulSoup

import ffs

logging.basicConfig(filename='indicators.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)


URL_TEMPLATE = "https://indicators.ic.nhs.uk/webview/velocity?v=2&mode=documentation&submode=ddi&study=http%3A%2F%2F172.16.9.26%3A80%2Fobj%2FfStudy%2FP{:05}"


def get_indicator(i, directory):
    """
    Returns a dict containing metadata extracted from the HTML, the HTML for
    the request will be cached by requests-cache, so we don't need to cache it
    outselves.
    """
    logging.info('Indicator ID: {}'.format(i))

    url = URL_TEMPLATE.format(i)
    logging.info('Requesting {}'.format(url))
    response = requests.get(url)
    logging.info(response.status_code)
    if response.status_code < 400:
        html = response.text

    result = {}
    if html:
        logging.info('Got HTML')
        soup = BeautifulSoup(html)
        data = soup.find(id="metadata")
        children = []
        if not data:
            logging.info("No data on {}".format(url))
            return

        for child in data.children:
            if hasattr(child, 'text'):
                clean = child.text.strip()
            else:
                clean = child.string.strip()
            if clean:
                children.append(clean)
        if children:
            for x in range(0, len(children), 2):
                if hasattr(children[x], 'text'):
                    key = children[x].text.strip().lower()
                else:
                    key = children[x].strip().lower()
                if hasattr(children[x+1], 'text'):
                    value = children[x+1].text.strip()
                else:
                    value = children[x+1].strip()
                if key == 'keyword(s)':
                    value = [tag for tag in value.split('\r\n')
                             if tag.strip()]
                if key == 'download(s)':
                    break
                result[key] = value
            links = data.find_all('a')
            sources = []
            for source in links:
                url = 'https://indicators.ic.nhs.uk' + source.attrs['href']
                description = source.text
                filetype = url[url.rfind('.') + 1:]
                sources.append({
                    'url': url,
                    'description': description.replace('.{}'.format(filetype), ''),
                    'filetype': filetype,
                })
            result['sources'] = sources
        else:
            logging.error('NO CONTENT FOUND')
    else:
        logging.error('UNABLE TO GET PAGE FOR {}'.format(i))
    return result


def scrape(workspace):
    result = []

    directory = ffs.Path(workspace) / 'indicators_raw'
    directory.mkdir()
    filename = directory / 'indicators.json'
    for i in range(1, 1699):
        indicator = get_indicator(i, directory)
        if indicator:
            result.append(indicator)
    json.dump(result, open(filename, 'wb'), indent=2)
    logging.info('Written results to {}'.format(filename))
