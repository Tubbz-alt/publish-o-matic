"""
This script takes the raw scraped Indicator data from the HSCIC indicator
portal and then curates them into NHSOF/CCGOIS groups, tags and renames them
so that they are useful for the way that NHSE Analysts actually think/work
"""
import sys

import ffs

import dc

DATA_DIR = ffs.Path.here()/'../data'

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))
 
dataset_from_indicator = lambda indicator: dc.ckan.action.package_show(id='hscic_indicator_' + indicator['unique identifier'].lower())

def is_indicator(indicator):
    """
    Predicate function to determine whether a dataset is in fact an
    indicator of the sort we're interested in 
    """
    return len([s for s in indicator['sources'] if s['description'] == 'Indicator specification']) > 0
        
def determine_framework(indicator):
    """
    Return the framework name
    """
    name = None
    fristurl = [s['url'] for s in indicator['sources'] if s['description'] == 'Indicator specification'][0]
    if 'Clinical Commissioning Group Indicators' in fristurl:
        name = 'CCGOIS'
    if 'Outcomes Framework' in fristurl:
        name = 'NHSOF'
    return name
        
def rename(indicator, newname):
    """
    Rename the INDICATOR to NEWNAME
    """
    dc.Dataset.rename(indicator, newname)
    return

def add_tag(indicator, tag):
    """
    Ensure that INDICATOR is tagged with TAG
    """
    dataset = dataset_from_indicator(indicator)
    return dc.Dataset.tag(dataset, tag)

def add_to_group(indicator, group):
    """
    Ensure that INDICATOR is in GROUP
    """
    group = group.lower()
    dataset = dataset_from_indicator(indicator)
    if [g for g in dataset['groups'] if g['name'] == group]:
        print 'Already in group', group
        return
    dc.ckan.action.member_create(
        id=group, 
        object=dataset['name'],
        object_type='package',
        capacity='member'
    )
    return

def curate_hscic_indicators():
    """
    Curate it! 
    """
    dc.ensure_group('NHSOF')
    dc.ensure_group('CCGOIS')
    
    indicators = DATA_DIR/'indicators.json'
    data = indicators.json_load()
    for indicator in data:
        if is_indicator(indicator):
            framework = determine_framework(indicator)
            number = indicator['title'].split(' ')[0]
            print framework, number
            unique_id = 'hscic_indicator_'+ indicator['unique identifier'].lower()
            print unique_id
            newname = u'{0} {1}'.format(framework, indicator['title'])
            rename(unique_id, newname)
            add_tag(indicator, framework)
            add_to_group(indicator, framework)
    return
        
def main():
    curate_hscic_indicators()
    return 0

if __name__ == '__main__':
    sys.exit(main())
