from load import main as main_load
from scrape import main as main_scrape
from transform import main as main_transform


def entrypoints():
    """
        scrapes and saves the MH annual bulletin, e.g.
        http://content.digital.nhs.uk/article/2021/Website-Search?productid=19123&q=Mental+Health+Bulletin%2c+Annual+Report&sort=Relevance&size=10&page=1&area=both#top

        and stores in the mhsds group
    """
    return {
        'scrape': main_scrape,
        'transform': main_transform,
        'load': main_load
    }
