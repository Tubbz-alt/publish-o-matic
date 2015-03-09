

#from load import main as main_load
#from transform import main as main_transform
from scrape import main as main_scrape

def entrypoints():
    return {
        'scrape': main_scrape,
        #'transform': main_transform,
        #'load': main_load
    }