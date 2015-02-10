#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This tool will run scrapers, if it can.  It also sets up a working area for them
so that they don't all have to have their own data folder. This can optionally be
cleaned up after each run.
'''
import os
import pkgutil
import shutil
import sys

from publish.lib.manifest import (get_scraper_names, get_scraper_entrypoints)

def should_run_task(name):
    """
    Given the name of a task, check the command line arguments to see if
    the task should be executed.  By default all tasks will be run, unless
    a switch is used to limit the task.  The switches are:
        --scrape     Only run the scrape task
        --transform  Only run the transform task
        --load       Only run the load task
    """
    assert name in ['scrape', 'transform', 'load']

    arg_count = len(sys.argv) - 1
    if arg_count == 1:
        return True
    return arg_count > 1 and '--{}'.format(name) in sys.argv

def usage(error):
    """ Explain to the user why it won't run """
    sys.stderr.write("{}\n\n".format(error))
    sys.stderr.write("Please choose from: \n\n\t")
    sys.stderr.write( "\n\t".join(scraper for scraper in get_scraper_names()))
    sys.stderr.write("\n\n")

def get_or_create_workspace(name):
    return '/tmp/{}'.format(name)

def main():
    """
    Main entry point, loads and runs the scraper once is has determined whether
    it can/should.
    """
    if len(sys.argv) == 1:
        usage("No scraper name was specified!")
        return sys.exit(1)

    scraper_name = sys.argv[1]
    if not scraper_name in get_scraper_names():
        usage("Could not find scraper '{}'".format(scraper_name))
        return sys.exit(1)


    if os.environ.get('REQ_DEV') == "1":
        import requests_cache
        print "Installing requests cache"
        requests_cache.install_cache('scraper_cache', expire_after=84200)

    entry_points = get_scraper_entrypoints(scraper_name)
    workspace = get_or_create_workspace(scraper_name)

    fail = False
    for task in ['scrape', 'transform', 'load']:
        if should_run_task(task) and task in entry_points:
            print "*" * 30, "Running {}".format(task)
            try:
                entry_points[task](workspace)
            except Exception as e:
                fail = True

                # TODO: Log e and notify someone...
                import traceback
                print traceback.format_exc()


    if not fail and len(sys.argv) == 2:
        # Cleanup the workspace ready for the next run only if we succeeded
        # so there's some forensic info for debugging
        shutil.rmtree(workspace)

