"""
Scrapes the HTML and dumps all of the data into the workspace ready
for the transform task to manipulate it into a format the CKAN can
understand.
"""
import ffs

DATA_DIR = None


def load():
    # Load the metadata in each directory of the DATA_DIR and process
    # it.
    for directory in DATA_DIR.ls():
        print directory


def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    load()

    return 0
