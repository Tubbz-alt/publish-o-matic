"""
Scrapes the friends and family test data at
http://www.england.nhs.uk/statistics/statistical-work-areas/friends-and-family-test/friends-and-family-test-data/
"""
import calendar
import datetime
import slugify
from collections import defaultdict


import requests
from bs4 import BeautifulSoup

from publish.lib.helpers import to_markdown
from publish.lib.encoding import fix_bad_unicode


TITLE_ROOT = "Friends and Family Test"


DESCRIPTION = [
    """
        The Friends and Family Test (FFT) is an important feedback tool that
        supports the fundamental principle that people who use NHS services
        should have the opportunity to provide feedback on their experience.
    """,
    """
        It asks people if they would recommend the services they have used and
        offers a range of responses. When combined with supplementary follow-up
        questions, the FFT provides a mechanism to highlight both good and poor
         patient experience. This kind of feedback is vital in transforming NHS
         services and supporting patient choice.
    """,
    """
        Since it was initially launched in April 2013, the FFT has been rolled
        out in phases to most NHS-funded services in England, giving all
        patients the opportunity to leave feedback on their care and treatment.
    """,
    """
        The FFT has produced around 25 million pieces of feedback so far- and
        the total rises by over a million a month - making it the biggest
        source of patient opinion in the world. Scores so far have told us
        that at least nine out of ten patients would recommend the services
        they used to their loved ones. Patient comments also identify areas
        where improvements can be made so that providers can make care and
        treatment better for everyone.
    """
]

FRIENDS_AND_FAMILTY_TEST_TYPES = [
    "FFT A&E",
    "FFT Ambulance (including PTS)",
    "FFT Community",
    "FFT Dental",
    "FFT GP",
    "FFT Inpatient",
    "FFT Maternity",
    "FFT Mental Health",
    "FFT Outpatient",
]


HISTORIC_DATA = 'https://www.england.nhs.uk/ourwork/pe/fft/friends-and-family-test-data/fft-data-historic'
CURRENT_DATA = "https://www.england.nhs.uk/ourwork/pe/fft/friends-and-family-test-data/"


def get_soup(url):
    return BeautifulSoup(requests.get(url).content)


class Resource(object):
    def get_month(self, some_date_str):
        for month in calendar.month_name:
            if month and month.lower() in some_date_str.lower():
                return month

    def get_year(self, some_date_str):
        for year in xrange(2010, 2030):
            # note the space
            lookup_year = " {}".format(year)
            if lookup_year in some_date_str:
                return year

    def __init__(self, friends_and_family_type, anchor):
        self.friends_and_family_type = friends_and_family_type
        self.url = anchor.attrs["href"]
        # horrific unicode mangling work
        link_title = anchor.get_text().encode('ascii', 'replace')
        split_link_title = link_title.replace(" ?", "").replace("?", " ")
        self.link_title = split_link_title
        self.year = self.get_year(self.link_title)
        self.month = self.get_month(self.link_title)

        # titles have things like revised on... then a date, lets strip that
        self.cleaned_title = " ".join(self.link_title.split(" ")[:2])
        self.name = self.url.split('/')[-1]
        self.format = self.url.rsplit(".", 1)[-1].upper()

    def to_dict(self):
        return dict(
            description=self.link_title,
            name=self.name,
            url=self.url,
            format=self.format
        )

    def get_key(self):
        return (self.cleaned_title, self.year)


def get_current_data():
    resources = []
    soup = get_soup(CURRENT_DATA)
    latest_data_h2 = soup.find(
        "h2", text="Organisational level tables (latest month)"
    )
    latest_data_container = latest_data_h2.find_next("ul")
    links = latest_data_container.find_all("a")
    for link in links:
        friends_and_family_type = link.get_text().split("-")[0].strip()
        resource = Resource(friends_and_family_type, link)
        resources.append(resource)
    return resources


def get_historic_data():
    soup = get_soup(HISTORIC_DATA)
    resources = []
    links = soup.find_all("a", {"class": "xls-link"})
    headers = soup.find_all("h3")

    for header in headers:
        friends_and_family_type = header.get_text()
        links = header.find_next("ul").find_all("a")
        for link in links:
            friends_and_family_type = link.find_previous("h3").get_text()
            resources.append(Resource(friends_and_family_type, link))
    return resources


def get_description():
    return to_markdown(
        fix_bad_unicode(unicode("\n".join([i.strip() for i in DESCRIPTION])))
    )


def aggregate_to_dataset(resources):
    """ We need to aggregate this by year and set titles
        appropiately
    """
    aggregate_dict = defaultdict(list)
    for resource in resources:
        aggregate_dict[resource.get_key()].append(resource)

    datasets = []
    description = get_description()
    this_year = datetime.date.today().year

    for k, v in aggregate_dict.iteritems():
        first_item = v[0]
        tags = [
            "Friends and Family",
            "Statistics",
            first_item.year,
            first_item.cleaned_title.replace('&',' and ')
        ]
        coverage_end_date = "{}-12-01".format(first_item.year)
        if first_item.year == this_year:
            months = list(calendar.month_name)[1:]
            latest_month = max(months.index(i.month) for i in v)
            _, last_day = calendar.monthrange(first_item.year, latest_month)
            if len(str(latest_month)) == 1:
                latest_month = "0{}".format(latest_month)

            coverage_end_date = "{0}-{1}-{2}".format(
                first_item.year, latest_month, last_day
            )

        datasets.append(dict(
            title=first_item.cleaned_title,
            name=slugify.slugify(first_item.cleaned_title).lower(),
            state="active",
            source="https://www.england.nhs.uk/ourwork/pe/fft/friends-and-family-test-data/",
            origin="https://www.england.nhs.uk/ourwork/pe/fft/friends-and-family-test-data/",
            frequency="Monthly",
            notes=description,
            tags=tags,
            resources=[i.to_dict() for i in v],
            groups=['faf'],
            coverage_start_date="{}-01-01".format(first_item.year),
            coverage_end_date=coverage_end_date
        ))
    return datasets


def scrape(workspace):
    resources = get_historic_data()
    resources.extend(get_current_data())
    resources = [resource for resource in resources if "Community" in resource.cleaned_title]
    return aggregate_to_dataset(resources)
