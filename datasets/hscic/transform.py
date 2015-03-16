"""
Transform the datasets and indicators into something that looks like
a CKAN package, and write them all out into a single output json file.
"""
import shutil

import ffs

from publish.lib.metadata import get_resource_path

def transform(workspace):
    """ Loads indicators.json and datasets.json and transforms them before
        writing to {workspace}/metadata.json """
    folder = ffs.Path(workspace)
    output_file = folder / "metadata.json"

    indicator_metadata = ffs.Path(workspace) / 'indicators_raw/indicators.json'
    datasets_metadata = ffs.Path(workspace) / 'datasets.json'

    # Move the files into the correct location
    new_indicators = get_resource_path("indicators.json")
    new_datasets = get_resource_path("datasets.json")

    shutil.copyfile(indicator_metadata, new_indicators)
    shutil.copyfile(datasets_metadata, new_datasets)


