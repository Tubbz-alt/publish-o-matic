# Publish-o-Matic

Takes data from places, and puts them into a "Data" "Catalogue"

## Automatic Installation

See the instructions in the https://github.com/nhsengland/iit-infrastructure/tree/master/ansible README.rst file.

## Manual Installation

1. Set up a virtualenv using your favourite tool for doing so, and activate it.

2. ```git clone https://github.com/nhsengland/publish-o-matic.git```

3. ```python setup.py install``` # or develop if you insist on it being changeable

4. See below for setting up cronjobs

5. To manually run a scraper do ``` run_scraper <NAME>``` where name is the name of a module in the datasets module.


**TODO**: Merge steps 2 and 3.




## Setting up a cronjob

I don't trust it yet ...

```
$ crontool > mycrontab

$ less mycrontab

** does it look sane? **

$ crontab mycrontab

```

How wrong can it be?

```
$ crontool | crontab
```


## Structure of this repository:

### ./datasets

Contains individual STL (Scrape, Transform, Load) procedures for curated datasets.

Each directory is expected to contain a data dir (For cached/retrieved data files) and three files:

* scrape.py - scrape the data files and metadata
* transform.py - make adjustments / additions to scraped metadata as required
* load.py - load the datasets into a CKAN instance.
