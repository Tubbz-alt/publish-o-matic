"""
Make transformations/adjustments/reorganisations of the ASCOF data
"""
import datetime
import json
import sys

import ffs
import re

HERE = ffs.Path.here()
DATA_DIR = HERE / 'data'

PHOF_SUMMARY = """The Public Health Outcomes Framework Healthy lives, healthy people: Improving outcomes and supporting transparency sets out a vision for public health, desired outcomes and the indicators that will help us understand how well public health is being improved and protected.

The framework concentrates on two high-level outcomes to be achieved across the public health system, and groups further indicators into four 'domains' that cover the full spectrum of public health. The outcomes reflect a focus not only on how long people live, but on how well they live at all stages of life.

The data published in the tool are the baselines for the Public Health Outcomes Framework, with more recent and historical trend data where these are available. The baseline period is 2010 or equivalent, unless these data are unavailable or not deemed to be of sufficient quality.

A list of indicators updated, for the most recent and previous releases can be found in the Public Health Outcomes Framework Collection within www.gov.uk.

Data are published as part of a quarterly update cycle in August, November, February and May. Exact dates will be announced on the www.gov.uk statistical release calendar and this website. Public Health Outcomes Framework baseline data will be revised and corrected in accordance with the Code of Practice for Official Statistics.

To provide comments and suggestions please e-mail phof.enquiries@phe.gov.uk."""

def add_metadata_to_ascof_datasets():
    metadata_file = DATA_DIR/'dataset.metadata.json'
    metadata = metadata_file.json_load()
    
    metadata['tags'] = ['PHOF', 'Public Health Outcomes Framework']
    metadata['title'] ='PHOF - Public Health Outcomes Framework'
    metadata['frequency'] = 'yearly'
    metadata['summary'] = PHOF_SUMMARY
    metadata['source'] = 'http://www.phoutcomes.info/public-health-outcomes-framework'
    
    metadata['coverage_beginning_date'] = '01/01/2000'
    metadata['coverage_ending_date'] = '31/12/2013'

    metadata_file.truncate()
    metadata_file << json.dumps(metadata, indent=2)
    return
        
def main():
    add_metadata_to_ascof_datasets()
    return 0

if __name__ == '__main__':
    sys.exit(main())







