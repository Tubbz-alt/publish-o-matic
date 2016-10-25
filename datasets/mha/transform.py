from publish.lib.upload import Uploader
from publish.lib.helpers import filename_for_resource, download_file
import json
import ffs


def upload(dataset_file, directory):
    datasets = dataset_file.json_load()
    u = Uploader("hscic")
    for dataset in datasets:
        for resource in dataset["resources"]:
            filename = filename_for_resource(resource)
            path = directory/filename
            download_file(resource['url'], path)
            resource["url"] = u.upload(path)
    dataset_file.truncate()
    dataset_file << json.dumps(datasets, indent=2)


def main(workspace):
    dataset_file = ffs.Path(workspace) / 'data/mha/dataset.metadata.json'
    directory = ffs.Path(workspace) / 'data/mha/'
    upload(dataset_file, directory)
