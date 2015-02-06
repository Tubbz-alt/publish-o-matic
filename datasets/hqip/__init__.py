

from load import main as main_load
from scrape import main as main_scrape

def entrypoints():
    return {
        'scrape': main_scrape,
        'load': main_load
    }