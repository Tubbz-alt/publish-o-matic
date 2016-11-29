import requests
from bs4 import BeautifulSoup
from publish.lib.helpers import anchor_to_resource, get_name_from_title
from datetime import datetime

ROOT = "http://www.england.nhs.uk/statistics/statistical-work-areas/eip-waiting-times/"
TITLE = "Early Intervention in Psychosis Waiting Times"
TAGS = ["Mental illness"]


def extract_links(page):
    links = page.article.find_all("a")
    result = {}
    for link in links:
        for ext in ["pdf", "xls", "csv"]:
            if ext in link.text.lower():
                result[link.text] = link
    return result


def get_description(page):
    # The description for this page is what follows the Background subheader
    # unfortunately there are other paragraphs, so we just take
    # what's between the first h3s
    article = page.article
    background = article.h3
    if not background.text == 'Background':
        raise Exception("Unable to find background")
    result = []
    for i in background.next_siblings:
        if i.name == "h3":
            break
        else:
            if str(i).strip():
                result.append(str(i))

    return BeautifulSoup("\n".join(result)).text


def get_date_range_from_link_titles(links):
    """ we look for links of the format

        'EIP Waiting Times - May 2016 (XLS, 160KB)'

        although with unicode this is

        'EIP Waiting Times Timeseries \u2013 May 2016 (XLS, 160KB)'

        and construct date from and date to by using the min max in this
        daterange
    """
    link_titles = links.keys()
    specific_links = [i for i in link_titles if "XLS" in i and "EIP Waiting Times" in i]
    date_links = []

    for link in specific_links:
        date_link = link[20:]
        date_link = link.split(u"\u2013")[1].strip()
        date_link = date_link.split("(XLS")[0].strip()
        date_links.append(datetime.strptime(date_link, "%B %Y").date())

    return min(date_links).isoformat(), max(date_links).isoformat()


def scrape(workspace):
    print "{0} with workspace {1}".format(TITLE, workspace)

    response = requests.get(ROOT)

    if response.status_code >= 400:
        raise Exception(
            "unable to access page {0} with {1}".format(
                ROOT, response.status_code
            )
        )

    page = BeautifulSoup(response.text)
    page.anchor
    links = extract_links(page)
    coverage_start_date, coverage_end_date = get_date_range_from_link_titles(
        links
    )
    return [dict(
        title=TITLE,
        notes=get_description(page),
        origin=ROOT,
        tags=TAGS,
        resources=[
            anchor_to_resource(v, title=k) for k, v in links.iteritems()
        ],
        coverage_start_date=coverage_start_date,
        coverage_end_date=coverage_end_date,
        groups=["mental-health-dashboard-oct-2016", "eip"],
        name=get_name_from_title(TITLE),
    )]
