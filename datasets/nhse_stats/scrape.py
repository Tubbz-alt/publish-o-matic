import os
import json

import ffs
import requests
import pkgutil

import topics


def main(workspace):
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    datasets = []

    name = os.environ.get('STAT')

    for importer, modname, ispkg in pkgutil.iter_modules(topics.__path__):
        if name and not name == modname:
            print "Skipping {} as single name {} specified".format(modname, name)
            continue

        if modname not in ['ipmm']:
            continue

        try:
            m = importer.find_module(modname).load_module(modname)
            datasets.extend(m.scrape( DATA_DIR ))
        except Exception, e:
            # Do not fail all scrapers just because one of them failed.
            # Log it, and carry on
            # TODO: Log it.
            print e
            pass

    json.dump(datasets, open(os.path.join(DATA_DIR, "metadata.json"), 'wb'))
    return 0
