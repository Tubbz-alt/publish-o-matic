
from datasets.hscic.hscic_datasets import scrape as datasets_scrape
from datasets.hscic.hscic_indicators import scrape as indicators_scrape




def main(workspace):
    #datasets_scrape(workspace)
    indicators_scrape(workspace)