"""
Create empty UNIFY datasets in an instance.
"""
import sys

import ffs
from slugify import slugify

import dc

DATA_DIR = ffs.Path.here()/'../data'


def ensure_unify_datasets_exist():
    """
    Read the unify datasets to create from the CSV file.

    1. Check if they exist.
    2. If they don't, create 'em.
    3. There is no step 3.
    4. Profit
    """
    dc.ensure_publisher('unify')
    unifyfile = DATA_DIR/'datasets.csv'
    with unifyfile.csv(header=True) as csv:
        for row in csv:
            if row.source == 'UNIFY2':
                dc.Dataset.create_or_update(
                    name=slugify(row.title).lower(),
                    title=row.title,
                    state='active',
                    private=row.public=='N', 
                    license_id='ogl',
                    url='http://data.england.nhs.uk',
                    owner_org='unify',
                    resources=[]
                )
                print slugify(row.title).lower()
    return

def main():
    """
    CLI ENTRYPOINT...
    """
    ensure_unify_datasets_exist()
    return 0

if __name__ == '__main__':
    sys.exit(main())
