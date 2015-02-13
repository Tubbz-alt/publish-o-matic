
from load import main as main_load
from scrape import main as main_scrape
#from transform import main as main_transform

def entrypoints():
    return {
        'scrape': main_scrape,
        'load': main_load
    }