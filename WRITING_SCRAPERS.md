# Writing scrapers

## Available weapons

* beautifulsoup4

* requests

* lxml

* cssselect


## Rules of engagement

### How to layout the code

Create a new module within the ```datasets``` module and name it after the scraper.  As the new module needs to be loadable, you should create a __init__.py, which should look something like the following to specify where/how the individual tasks can be run.

```python
from myfile import myfunctions

def endpoints():
    return {
        'scrape': myfunctions.scrape,
        'transform': myfunctions.transform,
        'load': myfunctions.load
    }
```

Not all of these are required if your scraper doesn't need one of the stages.  When called your functions will be passed a string, which will be the location of the scrapers workspace, a place where it can save files.  To make this work, and using the example above, your function should look like:

```python
def scrape(workspace):
    pass
```

In general you should have your scrape.py fetch the data, and turn into a format that closely resembles the CKAN dataset dictionary.  The transform.py should apply anything to the datasets that applies to all of them, such as specific tags - as well as moving the resources to S3 (and changing the url field).  load.py should then be responsible for pushing the data to CKAN.  This last step will eventually be pushed up into the publish-o-matic library so that you can use a generic CKAN loader.

### What are the entry points and how are they launched

To enable your scraper to be run, you need to add an entry in the setup.py file, which specifies the scraper name, and where the endpoints can be loaded from.  If you don't do this, your scraper won't be available.

### How does config get passed to the scrapers

Currently only the workspace location is passed to the scraper functions.  You need to handle your own config until this is implemented fully.


### Using dc

If you use dc for talking to CKAN, you need a ~/.dc.ini that looks a bit like:

```
[ckan]
url = http://localhost
api_key = 0000-0000-0000-0000
```

If you don't have this file, it'll crash and complain that it can't find it.

## Dis-orderly retreats (aka crashes)


