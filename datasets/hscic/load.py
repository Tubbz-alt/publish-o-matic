"""
Load all of the datasets and indicators into CKAN.
"""
import json

import ffs



def load(workspace):
    """ Loads metadata.json and sends them to the remote
        CKAN instance, either creating or updating packages """
    folder = ffs.Path(workspace)
    input_file = folder / "metadata.json"

    datasets = json.load(open(input_file, 'r'))