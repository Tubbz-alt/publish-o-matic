"""
Scrape Choose and book utilisation
"""
import json
import sys
import urllib

import ffs
from lxml.html import fromstring
import requests

DATA_DIR = ffs.Path.here()/'../data'

CAB14 = 'http://www.chooseandbook.nhs.uk/staff/bau/reports'
CAB13 = 'http://www.chooseandbook.nhs.uk/staff/bau/reports/archiveutil13'

CAB_DESC = """The Choose and Book Utilisation reports now have (from the report w/e 24/11/13) the estimated % weekly utilisation included.  Many end users of this data may be new to this metric so we felt some clarification may be required.

To calculate % utilisation we need a numerator, the number of Choose and Book referrals generated by referrers, and a denominator, the total of paper and Choose and Book referrals generated by referrers.  The numerator is derived direct from Choose and Book. The numerator is defined as the initial booking of a referral, excluding re-bookings.  The denominator is more difficult. The only dataset that currently exist nationally are the Monthly Activity Returns (MAR) from hospitals. This only covers first outpatient so utilisation calculations are limited to first outpatient referrals. 
The MAR data is approximately 6 - 8 weeks, including processing (to remove referrals such as MOD and dental) in arrears and is our definitive dataset for % utilisation. This data can be found on the 'Month Series' tab of the utilisation report and should be used for actual utilisation data.

In order to give a more up to date estimation of first outpatient utilisation, historic MAR data is used to 'predict' activity prior to the MAR data being available. It is this data that we are now including in the reports.  We need to stress that this is an estimation of activity and not actual activity and there will be some variation from actuals that would be reported later when the MAR data is available.  Please contact chooseandbook@nhs.net if you have any questions relating to these reports."""

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

def _astree(url):
    """
    Helper that returns a URL as a lxml tree
    """
    content = urllib.urlopen(url).read()
    dom = fromstring(content)
    dom.make_links_absolute(url)
    return dom

def fetch_weekly_utilisation():
    """
    Fetch the weekly utilisation data
    """
    allmeta = []
    for year, target in [('2014', CAB14), ('2013', CAB13)]:
        reportpage = _astree(target)
        links = reportpage.cssselect('a')
        weekly_links = [l for l in links if 'util' in l.get('href', '')]

        metadata = dict(
            title='Choose and Book Weekly Utilisation reports ' + year,
            url='http://www.chooseandbook.nhs.uk/staff/bau/reports',
            description=CAB_DESC,
            tags=['Choose and Book']
        )
        metadata['resources'] = [
            dict(
                url=l.get('href'),
                filetype='xls',
                description=l.text_content()
            ) for l in weekly_links
        ]
        allmeta.append(metadata)

    cabfile = DATA_DIR/'choose.and.book.json'
    cabfile << json.dumps(allmeta, indent=2)
    return
    
def main():
    fetch_weekly_utilisation()
    return 0

if __name__ == '__main__':
    sys.exit(main())

