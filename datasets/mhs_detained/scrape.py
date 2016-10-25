from bs4 import BeautifulSoup
from datetime import date
from publish.lib import digital_nhs_helpers
import json
import requests
import ffs

SEARCH_URL = "http://content.digital.nhs.uk/article/2021/Website-Search?q={search_term}&go=Go&area=both"
EXPECTED_TITLE = "Inpatients Formally Detained in Hospitals Under the Mental Health Act 1983 and Patients Subject to Supervised Community Treatment, England - {start_year}-{end_year}, Annual figures"


def get_possible_titles():
    """
        given the format of the MHA title, look for all reports since 2013
    """
    current_year = date.today().year
    result = []
    for start_year in xrange(2009, current_year):
        end_year = start_year + 1
        result.append(
            EXPECTED_TITLE.format(start_year=start_year, end_year=end_year)
        )

    return result


def get_data_set():
    titles = get_possible_titles()
    result = []

    for title in titles:
        search_url = SEARCH_URL.format(search_term=title)
        response = requests.get(search_url)
        page = BeautifulSoup(response.text)
        search_results = digital_nhs_helpers.load_json_results(page)
        for search_result in search_results:
            if search_result["title"] == title:
                result.append(digital_nhs_helpers.parse_to_dataset(search_result))

    return result


def main(workspace):
    dataset = get_data_set()
    digital_nhs_helpers.store_results_to_file(workspace, 'mhs_detained', dataset)
