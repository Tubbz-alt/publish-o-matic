from bs4 import BeautifulSoup
from publish.lib.helpers import get_name_from_title
import requests
import datetime
from publish.lib import digital_nhs_helpers


DATASETS = [
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland",
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/clinicalcommissioninggroupmidyearpopulationestimates",
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/localauthoritiesinenglandz1",
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/lowersuperoutputareamidyearpopulationestimates"
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/middlesuperoutputareamidyearpopulationestimates",
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/clinicalcommissioninggroupsinenglandtable3",
    "http://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/localauthoritiesinenglandz1",
]


def get_title(soup):
    title_tag = soup.find("h1", {"class": "page-intro__title"})
    unneeded = title_tag.find("span", {"class": "page-intro__type"}).get_text()
    return title_tag.get_text().replace(unneeded, "")


def get_notes(soup):
    # find the div that says "About this dataset" and get the next node
    descriptor_header = soup.find("h2", text="About this dataset")
    return descriptor_header.find_next("p").get_text()


def get_resource_from_link(link):
    return dict(
        url=make_link_absolute(link["href"]),
        format=link["href"].rsplit(".", 1)[1],
        description=None
    )


def get_resources(soup):
    download_header = soup.find("h2", text="Your download options")
    link_container = download_header.find_next("div")
    return [
        get_resource_from_link(i) for i in link_container.find_all("a") if i.has_attr("data-ga-event")
    ]


def make_link_absolute(link):
    return "http://www.ons.gov.uk{}".format(link)


def get_dataset(dataset_url):
    response = requests.get(dataset_url)
    return BeautifulSoup(response.text)


def get_first_dataset():
    return get_dataset(DATASETS[0])


def get_publication_date(soup):
    metadata = soup.find("div", {"class": "meta-wrap"})
    release_span = metadata.find("span", text="Release date: ")
    date_tag = release_span.parent.get_text().replace("Release date:", "").strip()
    dt = datetime.datetime.strptime(date_tag, "%d %B %Y")
    return dt.strftime("%B, %d %Y")


def scrape_datasets():
    result = []
    for dataset_url in DATASETS:
        soup = get_dataset(dataset_url)
        title = get_title(soup)
        name = get_name_from_title(title)
        result.append(dict(
            title=title,
            name=name,
            publication_date=get_publication_date(soup),
            notes=get_notes(soup),
            coverage_start_date=None,
            coverage_end_date=None,
            frequency=None,
            owner_org="ons",
            state="active",
            source=dataset_url,
            resources=get_resources(soup),
            tags=[]
        ))
        return result


def main(workspace):
    results = scrape_datasets()
    digital_nhs_helpers.store_results_to_file(workspace, "ons", results)
