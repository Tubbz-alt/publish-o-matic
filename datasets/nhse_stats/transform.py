import ffs


DATA_DIR = None

def transform():
    pass

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'
    DATA_DIR.mkdir()

    transform()

    return 0