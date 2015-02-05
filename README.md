# Publish-o-Matic

Takes data from places, and puts them into a "Data" "Catalogue"

## Installation


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



