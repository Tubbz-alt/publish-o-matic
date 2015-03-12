"""
Transform the datasets and indicators into something that looks like
a CKAN package, and write them all out into a single output json file.
"""
import ffs


def transform(workspace):
    """ Loads indicators.json and datasets.json and transforms them before
        writing to {workspace}/metadata.json """
    folder = ffs.Path(workspace)
    output_file = folder / "metadata.json"

    indicator_metadata = ffs.Path(workspace) / 'indicators_raw/indicators.json'
    datasets_metadata = ffs.Path(workspace) / 'datasets_raw/datasets.json'

    indicators = json.load(open(indicator_metadata, 'r'))
    datasets = json.load(open(datasets_metadata, 'r'))

    metadata = []

    for indicator in indicators:
        pass

    for dataset in datasets:
        pass

    json.dump(metadata, open(output_file, 'w'))