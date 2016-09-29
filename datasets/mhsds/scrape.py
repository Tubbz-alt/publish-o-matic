from datetime import date, timedelta
import logging
import json
import ffs
from bs4 import BeautifulSoup
import requests
from publish.lib import digital_nhs_helpers


logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG
)

URL = "http://content.digital.nhs.uk/article/2021/Website-Search?q=mhsds-monthly-data-file-{0}+{1}+{2}&go=Go&area=both"


def get_next_month_number(month_number):
    return (month_number % 12) + 1


def get_month_name(month_number):
    today = date.today()
    return date(today.year, month_number, 1).strftime("%B")


def get_search_url(month, year):
    """
        we're looking for files that look like
        Mental Health Services Monthly Statistics: Final January, Provisional February 2016

        search urls therefore look something like
        http://content.digital.nhs.uk/article/2021/Website-Search?q=mhsds-monthly-data-file+May&go=Go&area=both

        its difficult to know what these will look like in December, I'm assuming they'll use the current year
        at some point
    """
    month_name = get_month_name(month)
    next_month = get_next_month_number(month)
    next_month_name = get_month_name(next_month)
    return URL.format(month_name, next_month_name, year)


def load_month(month, year):
    url = get_search_url(month, year)
    response = requests.get(url)

    if response.status_code >= 400:
        raise Exception(
            "unable to access page {0} with {1}".format(
                url, response.status_code
            )
        )

    page = BeautifulSoup(response.text)
    try:
        result = digital_nhs_helpers.load_json_results(page)
    except digital_nhs_helpers.UnableToFindJson:
        raise Exception("unable to load json results for {}".format(url))

    if not result:
        logging.info('No results for month {}'.format(
            get_month_name(month)
        ))

        return
    elif len(result) > 1:
        expected_title = "Final {}".format(get_month_name(month))
        result = [i for i in result if expected_title in i["title"]]
        if len(result) > 1:
            raise Exception("found multiple results for {0} {1}".format(month, year))

    return digital_nhs_helpers.parse_to_dataset(result[0])


def get_date_months_ago(number_of_months):
    today = date.today()
    year = today.year
    month = today.month - number_of_months
    if month < 1:
        month = 12 + month
        year = year - 1

    return date(year, month, 1)


def get_the_last_6_months():
    result = []
    for i in xrange(6, -1, -1):
        for_date = get_date_months_ago(i)
        dataset = load_month(for_date.month, for_date.year)

        # if the data set for this month hasn't been published
        # it will be ignored
        if dataset:
            result.append(dataset)

    return result


def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'
    dataset_dir = DATA_DIR/'mhsds'
    dataset_dir.mkdir()
    metadata_file = dataset_dir/'dataset.metadata.json'
    if metadata_file:
        metadata_file.truncate()
    dataset = get_the_last_6_months()
    metadata_file << json.dumps(dataset, indent=2)
