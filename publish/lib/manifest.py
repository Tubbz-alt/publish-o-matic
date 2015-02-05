# -*- coding: utf-8 -*-

'''
Provides information about scrapers to give to the scrapers when they need it.
'''
from pkg_resources import iter_entry_points


def get_scraper_names():
    """
    For now, gets all the scrapers by finding all the modules within
    the datasets module.  Later, will pull this from a manifest/entrypoint
    where config etc is stored.
    """
    return [ep.name for ep in iter_entry_points(group='scrapers', name=None)]

def get_scraper_entrypoints(name):
    """
    For the named scraper, try and load the entrypoints that it
    has defined for each type of task. We expect back a dictionary
    containing the task name and a function for that task.  If a task
    is missing, then it will just be skipped.
    """
    entry_point = list(iter_entry_points(group='scrapers', name=name))
    if not entry_point:
        raise ImportError("Can't load the {} endpoints".format(name))
    endpoint_func = entry_point[0].load()
    return endpoint_func()