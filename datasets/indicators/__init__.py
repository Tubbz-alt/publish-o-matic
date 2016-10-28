from scrape import main as main_scrape
from functools import partial
from publish.lib import digital_nhs_helpers

SCRAPER_NAME = "indicators"
GROUP = "ccgois"
PUBLISHER = "hscic"


def entrypoints():
    """
        scrapes and saves the MH annual bulletin, e.g.
        scrapes the Improving Access to Psychological Therapies Report, e.g.
        http://content.digital.nhs.uk/catalogue/PUB21229

        and stores in the iapt group
    """

    # creates a function that uploads to S3 with this scraper
    transform = partial(
        digital_nhs_helpers.upload_resource_from_file,
        SCRAPER_NAME  # scraper name
    )

    # creates a function that uploads to S3 with this scraper, publisher, and group
    load = partial(
        digital_nhs_helpers.load_dataset_to_ckan,
        SCRAPER_NAME,  # scraper name
        PUBLISHER,  # publisher
        GROUP  # group
    )
    return {
        'scrape': main_scrape,
        'transform': transform,
        'load': load
    }
