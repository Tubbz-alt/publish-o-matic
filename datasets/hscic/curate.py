"""
A tool to curate datasets/indicators and determine how they should
be grouped/tagged etc
"""
from publish.lib.helpers import hd

class Curator(object):



    def __init__(self, dataset):
        self.dataset = dataset
        self.tags = []
        self.groups = []
        self.types = ['CCGOIS', 'NHSOF', 'HES', 'SHMI', 'IAPT']

    def get_tags(self):
        if self.tags:
            return self.tags

        return self.tags

    def get_title_prefix(self):
        for g in self.get_groups():
            if g in self.types:
                return g
        return None

    def get_groups(self):
        if self.groups:
            return self.groups

        if 'Improving Access to Psychological Therapies' in self.dataset['title']:
            self.groups.append('IAPT')


        if 'Hospital Episode Statistics' in self.dataset['title']:
            self.groups.append('HES')

        if 'SHMI' in self.dataset['title']:
            self.groups.append('SHMI')

        # Check indicator specific data....
        firsturl = hd([s['url'] for s in self.dataset.get('sources',[]) if s['description'] == 'Indicator specification'])
        if firsturl:
            if 'Clinical Commissioning Group Indicators' in firsturl:
                self.groups.append('CCGOIS')
            if 'Outcomes Framework' in firsturl:
                self.groups.append('NHSOF')

        for a in self.dataset.get('sources', []):
            if 'Quality and Outcomes Framework' in a['description']:
                self.groups.append('QOF')

        self.groups = list(set(self.groups))

        if self.groups:
            print "***" * 20
            print "Curated into a group {}".format(self.groups)
            print "***" * 20

        return self.groups