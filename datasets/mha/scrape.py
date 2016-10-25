from bs4 import BeautifulSoup
from datetime import date
from publish.lib import digital_nhs_helpers
import json
import requests
import ffs

SEARCH_URL = "http://content.digital.nhs.uk/article/2021/Website-Search?q=Mental+Health+Bulletin%2C+Annual+Report&go=Go&area=both"

# e.g. "Mental Health Bulletin, Annual Report - 2014-15"
MHA_TITLE = "Mental Health Bulletin, Annual Report - {start_year}-{end_year}"


def get_possible_titles():
    """
        given the format of the MHA title, look for all reports since 2013
    """
    current_year = date.today().year
    result = []
    for start_year in xrange(2013, current_year):
        end_year = str(start_year + 1)[-2:]
        result.append(MHA_TITLE.format(start_year=start_year, end_year=end_year))

    return result


def get_data_set():
    titles = get_possible_titles()
    response = requests.get(SEARCH_URL)
    page = BeautifulSoup(response.text)
    search_results = digital_nhs_helpers.load_json_results(page)
    result = []
    for search_result in search_results:
        if search_result["title"] in titles:
            result.append(digital_nhs_helpers.parse_to_dataset(search_result))

    return result


def main(workspace):
    dataset = get_data_set()
    digital_nhs_helpers.store_results_to_file(workspace, "mha", dataset)
