

from scrape import main as main_scrape

def entrypoints():
    return {
        'scrape': main_scrape,
    }