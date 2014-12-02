## Publish-o-Matic

Takes data from places, and puts them into a "Data" "Catalogue"

## Structure of this repository: 

### ./datasets

Contains individual STL (Scrape, Transform, Load) procedures for curated datasets. 

Each directory is expected to contain a data dir (For cached/retrieved data files) and three files: 

scrape.py - scrape the data files and metadata
transform.py - make adjustments / additions to scraped metadata as required
load.py - load the datasets into a CKAN instance. 
