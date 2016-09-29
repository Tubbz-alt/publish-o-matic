# helps that help with the content.digital.nhs.uk site
import json
from publish.lib.helpers import to_markdown, get_name_from_title
import datetime


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
