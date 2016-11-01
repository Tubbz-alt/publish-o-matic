from publish.lib import digital_nhs_helpers
from publish.lib import indicators_helpers

SCRAPER_NAME = "ccgois_indicators"


def main(workspace):
    result = indicators_helpers.extract_indicators("CCG Outcomes Indicator Set")
    digital_nhs_helpers.store_results_to_file(
        workspace,
        SCRAPER_NAME,
        result
    )
