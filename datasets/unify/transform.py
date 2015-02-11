"""
Make transformations/adjustments/reorganisations of the unify data,
making sure we add relevant tags etc
"""
import datetime
import json
import sys

import ffs
import re

DATA_DIR = None



def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    return 0

