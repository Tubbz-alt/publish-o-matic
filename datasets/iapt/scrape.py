from publish.lib import digital_nhs_helpers
from bs4 import BeautifulSoup
import ffs
import json
# A data scraper for Improving Access to Psychological


# example titles
# "Improving Access to Psychological Therapies Report, April 2016 Final, May 2016 Primary + Quarter 3 2015/16"
# "Improving Access to Psychological Therapies Report, January 2016 Final, February 2016 Primary and Quarter 3 2015/16"
# "Improving Access to Psychological Therapies Report, June 2016 Final, July 2016 Primary and most recent quarterly data (Quarter 4 2015/16)"
# "Improving Access to Psychological Therapies Report, May 2016 Final, June 2016 Primary and most recent quarterly data (Quarter 4 2015-16)"
# "Improving Access to Psychological Therapies Report, March 2016 Final, April 2016 Primary and most recent quarterly data (Quarter 3 2015/16)"

# note subtley different formatting, also there are a lot of false friends..

import requests


SEARCH_URL = "http://content.digital.nhs.uk/article/2021/Website-Search?q=%22Improving+Access+to+Psychological+Therapies+Report%22&sort=Relevance&size=100&page=1&area=both#top"
STARTS_WITH = "Improving Access to Psychological Therapies Report"


def filter_search_results(search_results):
    return [sr for sr in search_results if sr["title"].startswith(STARTS_WITH)]


def main(workspace):
    search_page = BeautifulSoup(requests.get(SEARCH_URL).text)
    search_results = digital_nhs_helpers.load_json_results(search_page)
    valid_search_results = filter_search_results(search_results)
    dataset = []
    for valid_search_result in valid_search_results:
        dataset.append(digital_nhs_helpers.parse_to_dataset(
            valid_search_result,
        ))

    DATA_DIR = ffs.Path(workspace) / 'data'
    dataset_dir = DATA_DIR/'iapt'
    dataset_dir.mkdir()
    metadata_file = dataset_dir/'dataset.metadata.json'
    if metadata_file:
        metadata_file.truncate()
    metadata_file << json.dumps(dataset, indent=2)
