import json
import sys

import ckanapi
import dc
import ffs
import slugify




def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    dc.ensure_publisher('hscic')

