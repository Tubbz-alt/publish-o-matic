import re
import requests
import datetime
from bs4 import BeautifulSoup
from publish.lib.helpers import get_name_from_title
from publish.lib import digital_nhs_helpers

# so the wonderful https://indicators.hscic.gov.uk/webview/
# is not going to make our life easy
# not only is it a lot of iframes but even the navigation steps
# are loaded in dynamically
# therefore we'll hit the top level of their navigation tree
# then all the bits underneath until we create our own tree
# then go after what we want...

# the top level tree is split into different domains

# the top level nav tree url
INDICATORS_ROOT = "https://indicators.hscic.gov.uk"
NAV_TREE_URL_STRUCTURE = "{}/webview/velocity?v=2&mode=tree&submode=catalog"
NAV_TREE_URL = NAV_TREE_URL_STRUCTURE.format(INDICATORS_ROOT)

NAV_TREE_URL_BEGINNING = "openRootCatalogWithoutCatalogComment(this, '"
NAV_TREE_URL_END = "', false);"
SCRAPER_NAME = "indicators"



def make_absolute(relative_path):
    return "{0}{1}".format(INDICATORS_ROOT, relative_path)


def get_ccg_navigation():
    """ we only care about the ccg information, ignore the rest
    """
    nav_tree = BeautifulSoup(requests.get(NAV_TREE_URL).text)
    ccg_outcomes_set = nav_tree.find("a", title="CCG Outcomes Indicator Set")
    return ccg_outcomes_set.findNext("div").find("ul")


def get_subnavigation_for_domain():
    """ iterates over the nodes just under the ccg navigation set
        (at present thats Domain 1 -5) and returns their links
    """
    all_links = get_ccg_navigation().find_all("a", class_="nodetext")
    # at the moment we only care about the ccg links which begin with 'Domain'
    sub_tree_urls = []

    for link in all_links:
        click = link.attrs["onclick"]
        i = click.replace(NAV_TREE_URL_BEGINNING, "")
        i = i.replace(NAV_TREE_URL_END, "")
        sub_tree_urls.append(make_absolute(i))

    return sub_tree_urls


def get_ccg_articles():
    """ iterate through everything in the ccg domain set
        and return all links to the individual articles
    """
    result = []
    for link in get_subnavigation_for_domain():
        soup = BeautifulSoup(requests.get(link).text)
        leaf_links = soup.find_all("a", class_="nodetext")
        for leaf_link in leaf_links:
            result.append(make_absolute(leaf_link.attrs["href"]))
    return result


def get_publication_date(unparsed):
    dt = datetime.datetime.strptime(unparsed, "%b-%y")
    return dt.strftime("%Y-%m-%d")

def process_ccg_articles(article_link):
    """ take in an article and translate it into something
        we can upload to ckan

        example article link
        https://indicators.hscic.gov.uk/webview/velocity;jsessionid=17FEDE2398D364B309E50A29824595F6?v=2&mode=documentation&submode=ddi&study=http%3A%2F%2F192.168.229.23%3A80%2Fobj%2FfStudy%2FP01877
    """
    article = BeautifulSoup(requests.get(article_link).text)
    title = article.find(text=re.compile("Title"))
    title = title.findNext(class_="ddicontent").text.strip()

    description = article.find(text=re.compile("Definition"))
    description = description.findNext(class_="ddicontent").text.strip()

    all_keywords = article.find(class_="keywordnode").find_all("li")
    publication_date = article.find(text=re.compile("Current version uploaded"))
    publication_date = publication_date.findNext(
        class_="ddicontent"
    ).text.strip()
    if publication_date == "TBC":
        publication_date = None
    else:
        publication_date = get_publication_date(publication_date)
    tags = [i.text.strip() for i in all_keywords]
    downloads = article.find(text=re.compile("Download")).find_all_next("a")
    resources = []
    for download in downloads:
        title = download.text
        link = make_absolute(download.attrs["href"])
        file_format = link.rsplit(".", 1)[-1]
        resources.append(dict(
            description="",
            title=download.text,
            format=file_format,
            url=link
        ))

    return dict(
        name=get_name_from_title(title),
        title=title,
        notes=description,
        source=article_link,
        publication_date=publication_date,
        tags=tags,
        owner_org='hscic',
        resources=resources,
        frequency='Quarterly',
        coverage_start_date=None,
        coverage_end_date=None,
    )


def main(workspace):
    articles = get_ccg_articles()
    result = []
    for article in articles:
        result.append(process_ccg_articles(article))
    digital_nhs_helpers.store_results_to_file(
        workspace,
        SCRAPER_NAME,
        result
    )
