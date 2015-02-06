
import os

def get_resource_path(resource_name):
    """
    Given a relative path, such as data/indicators.json will return the full path
    to the resource in the metadata directory.
    """
    root = os.path.dirname(__file__)
    f = os.path.join(root, os.path.pardir, os.path.pardir, "metadata", resource_name)
    return os.path.abspath(f)

def get_resource_file(resource_name):
    """
    Given a relative path, such as data/indicators.json will return a file-like object
    opened for reading.  It is the responsibility of the caller to close the file.
    """
    return open(get_resource_path(resource_name), 'r')