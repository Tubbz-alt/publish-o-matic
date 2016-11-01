"""
 helpers to scrape from the https://indicators.hscic.gov.uk/webview/ site
"""
import datetime
import requests
import re

from bs4 import BeautifulSoup

from publish.lib.helpers import get_name_from_title

INDICATORS_ROOT = "https://indicators.hscic.gov.uk"
NAV_TREE_URL_STRUCTURE = "{}/webview/velocity?v=2&mode=tree&submode=catalog"
NAV_TREE_URL = NAV_TREE_URL_STRUCTURE.format(INDICATORS_ROOT)
NAV_TREE_URL_BEGINNING = "openRootCatalogWithoutCatalogComment(this, '"
NAV_TREE_URL_END = "', false);"


def make_absolute(relative_path):
    return "{0}{1}".format(INDICATORS_ROOT, relative_path)


def extract_link(some_anchor):
    """ this site just puts the links in raw js in the on click event
        strip them out
    """
    js_link = some_anchor.attrs["onclick"]
    index = js_link.index("/webview")
    js_link = js_link[index:]
    js_link = js_link.replace(NAV_TREE_URL_END, "")
    return make_absolute(js_link)


def get_link(some_url):
    return BeautifulSoup(requests.get(some_url).text)


def get_leaf_node(parent_node, already_seen):
    results = []
    links = parent_node.find_all("a", class_="nodetext")

    for link in links:
        if "href" in link.attrs:
            results.append(make_absolute(link.attrs["href"]))
            break
        else:
            url = extract_link(link)
            sub_nav = get_link(url)
            sub_nav.findNext("div", class_="nextlevel")
            results.extend(get_leaf_node(sub_nav, already_seen))

    return results


def get_navigation(title):
    nav_tree = BeautifulSoup(requests.get(NAV_TREE_URL).text)
    nav_tree = nav_tree.find(class_="browsetree").find(class_="browsetree")
    nav_link = extract_link(nav_tree.find("a", title=title))
    return get_leaf_node(get_link(nav_link), {nav_link})


def get_publication_date(unparsed):
    dt = datetime.datetime.strptime(unparsed, "%b-%y")
    return dt.strftime("%Y-%m-%d")


def extract_indicators(title):
    links = get_navigation(title)
    results = []

    links = links[:1]
    for link in links:
        results.append(process_article(link))

    return [r for r in results if r]


def process_article(article_link):
    """ take in an article and translate it into something
        we can upload to ckan

        example article link
        https://indicators.hscic.gov.uk/webview/velocity;jsessionid=17FEDE2398D364B309E50A29824595F6?v=2&mode=documentation&submode=ddi&study=http%3A%2F%2F192.168.229.23%3A80%2Fobj%2FfStudy%2FP01877
    """
    article = get_link(article_link)
    if not article.find(id="toptitle").text.lstrip().startswith("Dataset:"):
        # all pages have dataset: in them apart from pages we don't want like
        # https://indicators.hscic.gov.uk/webview/velocity;jsessionid=887A142248AC0B0B22B4D1FBE83C9795?mode=documentation&submode=catalog&catalog=http%3A%2F%2F192.168.229.23%3A80%2Fobj%2FfCatalog%2FCatalog329
        return
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
