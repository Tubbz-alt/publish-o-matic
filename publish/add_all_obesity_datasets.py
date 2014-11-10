"""
Return all of the datasets that match "Obesity" and add them to the 
federated obesity group.
"""
import sys

import dc

def put_into_group():
    obeses = dc.ckan.action.package_search(q='obesity', rows=10000)

    for package in obeses['results']:
        if [g for g in package['groups'] if g['name'] == 'federated-uk-us-obesity-data']:
            print 'Already in group -', package['name']
            continue
        print 'Adding', package['name']
        dc.ckan.action.member_create(
            id='federated-uk-us-obesity-data', 
            object=package['name'],
            object_type='package',
            capacity='member'
        )
        print 'Done'

    return

def main():
    put_into_group()
    return 0

if __name__ == '__main__':
    sys.exit(main())
