# helps that help with the content.digital.nhs.uk site
import json
from publish.lib.upload import Uploader
from publish.lib.helpers import (
    to_markdown, get_name_from_title, filename_for_resource, download_file
)
import datetime
import dc
import ffs


class UnableToFindJson(Exception):
    pass


def load_json_results(page):
    """ looks for the json results div, cleans it and parses
    """
    json_results_div = page.find(id="jsonresults")

    if not json_results_div:
        if "Results 0 - 0 of 0" not in page.text:
            raise UnableToFindJson(
                "unable to find json results"
            )
        else:
            return
    unparsed_results = json_results_div.find('script').text.strip()
    unparsed_results = unparsed_results.lstrip("var jsonProducts =")
    unparsed_results = unparsed_results.rstrip(";")
    return json.loads(unparsed_results)


def get_start_stop_date_from_dataset(parsed_json):
    start, stop = parsed_json["date_range"].split(" to ")
    return (
        datetime.datetime.strptime(start, "%B %d, %Y").date().isoformat(),
        datetime.datetime.strptime(stop, "%B %d, %Y").date().isoformat(),
    )


def parse_to_dataset(parsed_json, **kwargs):
    """ translates the json found in the load results
        into a ckan data set format
    """

    dataset = dict(
        title=parsed_json["title"],
        name=get_name_from_title(parsed_json["title"]),
        state="active",
        source=parsed_json["source"],
        tags=parsed_json["keywords"],
        publication_date=parsed_json["publication_date"],
        owner_org="hscic",
        frequency="Monthly",
    )

    dataset["notes"] = to_markdown(parsed_json['summary'])
    if 'key_facts' in parsed_json:
        key_facts = '\n\nKEY FACTS:\n' + ''.join(parsed_json['key_facts'])
        dataset["notes"] += key_facts

    dataset["coverage_start_date"], dataset["coverage_end_date"] = get_start_stop_date_from_dataset(
        parsed_json
    )

    resources = []

    for source in parsed_json["sources"]:
        resources.append(dict(
            description=source["description"],
            format=source["filetype"],
            url=source["url"]
        ))

    dataset["resources"] = resources

    dataset.update(kwargs)
    return dataset


def store_results_to_file(workspace, scraper_name, dataset):
    """ Take a datset and store it as a json structure in a file
    """
    data_dir = ffs.Path(workspace) / 'data'
    dataset_dir = data_dir/scraper_name
    dataset_dir.mkdir()
    metadata_file = dataset_dir/'dataset.metadata.json'
    if metadata_file:
        metadata_file.truncate()
    metadata_file << json.dumps(dataset, indent=2)


def upload_resource_from_file(scraper_name, workspace, uploader='hscic'):
    """
        assumes that we've got a dataset taken from store_results_to_file
        in the format produced by parse_to_dataset, it will iterate
        over that list from that file and save all resources to S3
    """
    workspace_path = ffs.Path(workspace)
    relative_json_file = 'data/{}/dataset.metadata.json'.format(scraper_name)
    relative_json_dir = 'data/{}/'.format(scraper_name)
    dataset_file = workspace_path / relative_json_file
    directory = workspace_path / relative_json_dir
    datasets = dataset_file.json_load()
    u = Uploader(uploader)
    for dataset in datasets:
        for resource in dataset["resources"]:
            filename = filename_for_resource(resource)
            path = directory/filename
            download_file(resource['url'], path)
            resource["url"] = u.upload(path)
    dataset_file.truncate()
    dataset_file << json.dumps(datasets, indent=2)


def _load_data(datasets, publisher, extra_tags):
    for metadata in datasets:
        tags = metadata['tags'] + extra_tags
        resources = [
            dict(
                description=r['description'],
                name=r['url'].split('/')[-1],
                format=r['format'],
                url=r['url']
            )
            for r in metadata['resources']
        ]
        dc.Dataset.create_or_update(
            name=metadata["name"],
            title=metadata['title'],
            state='active',
            license_id='uk-ogl',
            notes=metadata['notes'],
            origin=metadata['source'],
            tags=dc.tags(*tags),
            resources=resources,
            owner_org=publisher,
            coverage_start_date=metadata['coverage_start_date'],
            coverage_end_date=metadata['coverage_end_date'],
            extras=[
                dict(
                    key='publication date',
                    value=metadata['publication_date']
                ),
                # note when we move to CKAN 2.5 this should be changed to a kwarg
                dict(key='frequency', value=metadata['frequency']),
            ]
        )


def _group_data(datasets, group):
    for metadata in datasets:
        dataset = dc.ckan.action.package_show(id=metadata["name"])

        if [g for g in dataset['groups'] if g['name'].lower() == group]:
            print 'Already in group', g

        else:
            dc.ckan.action.member_create(
                id=group,
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )


def load_dataset_to_ckan(scraper_name, publisher, group, workspace, extra_tags=None):
    """
        assumes that we've got a dataset taken from store_results_to_file
        in the format produced by parse_to_dataset, it will iterate
        over that list from that file and saves them as datasets to ckan
    """
    if not extra_tags:
        extra_tags = []
    relative_json_file = 'data/{}/dataset.metadata.json'.format(scraper_name)
    dataset_file = ffs.Path(workspace) / relative_json_file
    datasets = dataset_file.json_load()
    _load_data(datasets, publisher, extra_tags)
    _group_data(datasets, group)
    dc.ensure_publisher(publisher)
    dc.ensure_group(group)
