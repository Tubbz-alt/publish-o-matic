#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This tool iterates through all of the scrapers in the datasets module
and creates a cron-task for each one.
'''
import os
import pkgutil
import random
import sys


def get_launch_binary():
    this_location = sys.argv[0]
    return os.path.join(os.path.dirname(this_location), "run_scraper")

def get_scrapers():
    """
    For now, gets all the scrapers by finding all the modules within
    the datasets module.  Later, will pull this from a manifest/entrypoint
    where config etc is stored.
    """
    return [name for _, name, _ in pkgutil.iter_modules(['datasets'])]

def get_random_hours_and_minutes():
    random.seed()
    return random.choice(xrange(0, 23)), random.choice(xrange(0, 60, 5))

def main():
    binary = get_launch_binary()
    for scraper in get_scrapers():
        cli = "{cmd} {scraper}".format(cmd=binary, scraper=scraper )
        hour, minute = get_random_hours_and_minutes()
        crontime = "{} {} * * * {}".format(minute, hour, cli)
        print crontime