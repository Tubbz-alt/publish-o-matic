"""
Load the unify datasets into a CKAN instance
"""
import sys

import dc
import ffs
import slugify

DATA_DIR = None


def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    return 0
