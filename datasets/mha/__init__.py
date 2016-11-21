from scrape import main as main_scrape
from functools import partial
from publish.lib import digital_nhs_helpers

GROUP = "mental-health-dashboard"
EXTRA_TAGS = ["Mental Health"]


def entrypoints():
    """
        scrapes and saves the MH annual bulletin, e.g.
        http://content.digital.nhs.uk/article/2021/Website-Search?productid=19123&q=Mental+Health+Bulletin%2c+Annual+Report&sort=Relevance&size=10&page=1&area=both#top

        and stores in the mhsds group
    """

    # creates a function that uploads to S3 with this scraper
    transform = partial(
        digital_nhs_helpers.upload_resource_from_file,
        "mha" # scraper name
    )

    # creates a function that uploads to S3 with this scraper, publisher, and group
    load = partial(
        digital_nhs_helpers.load_dataset_to_ckan,
        "mha",  # scraper name
        "hscic",  # publisher
        GROUP,  # group
        extra_tags=EXTRA_TAGS
    )
    return {
        'scrape': main_scrape,
        'transform': transform,
        'load': load
    }
