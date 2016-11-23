from scrape import main as main_scrape
from functools import partial
from publish.lib import digital_nhs_helpers

GROUP = "office-of-national-statistics"
SCRAPER_NAME = "ons"
PUBLISHER = "ons"
EXTRA_TAGS = ["Population Estimates"]

# creates a function that uploads to S3 with this scraper
transform = partial(
    digital_nhs_helpers.upload_resource_from_file,
    SCRAPER_NAME
)

load = partial(
    digital_nhs_helpers.load_dataset_to_ckan,
    SCRAPER_NAME,  # scraper name
    PUBLISHER,  # publisher
    GROUP,  # group
    extra_tags=EXTRA_TAGS
)


def entrypoints():
    return {
        'scrape': main_scrape,
        'transform': transform,
        'load': load
    }
