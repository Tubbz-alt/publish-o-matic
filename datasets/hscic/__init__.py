

from load import load
from transform import transform
from scrape import main as main_scrape

def entrypoints():
    return {
        'scrape': main_scrape,
        'transform': transform,
        'load': load
    }