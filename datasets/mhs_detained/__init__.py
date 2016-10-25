from scrape import main as main_scrape
from functools import partial
from publish.lib import digital_nhs_helpers


def entrypoints():
    """
        scrapes the annual figures for the number of people
        detained under the mental health act

        e.g. http://content.digital.nhs.uk/catalogue/PUB18803
    """

    # creates a function that uploads to S3 with this scraper
    transform = partial(
        digital_nhs_helpers.upload_resource_from_file,
        "mhs_detained"  # scraper name
    )

    # creates a function that uploads to S3 with this scraper, publisher, and group
    load = partial(
        digital_nhs_helpers.load_dataset_to_ckan,
        "mhs_detained",  # scraper name
        "hscic",  # publisher
        "mhs-detained"  # group
    )
    return {
        'scrape': main_scrape,
        'transform': transform,
        'load': load
    }
