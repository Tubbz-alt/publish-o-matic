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

from publish.lib.manifest import get_scraper_names

def get_launch_binary():
    this_location = sys.argv[0]
    path = os.path.join(os.path.dirname(this_location), "run_scraper")
    return os.path.abspath(path)

def get_dmswitch_binary():
    this_location = sys.argv[0]
    path = os.path.join(os.path.dirname(this_location), "dmswitch")
    return os.path.abspath(path)

def get_random_hours_and_minutes():
    random.seed()
    return random.choice(xrange(0, 23)), random.choice(xrange(0, 60, 5))

def main():
    binary = get_launch_binary()
    dmswitch = get_dmswitch_binary()
    for scraper in get_scraper_names():
        cli = "{cmd} {scraper}  > /var/log/publishomatic/{scraper}.log && {dms} --switch {scraper}"\
            .format(cmd=binary, scraper=scraper, dms=dmswitch)
        hour, minute = get_random_hours_and_minutes()
        crontime = "{} {} */2 * * {}".format(minute, hour, cli)
        print crontime

    switch = "{dms} --check 48"\
            .format(dms=dmswitch)
    hour, minute = get_random_hours_and_minutes()
    crontime = "0 0 */2 * * {}".format(switch)
    print crontime