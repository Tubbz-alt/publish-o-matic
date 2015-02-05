import json

fields = [
    "coverage_start_date",
    "coverage_end_date",
]

domains = [
    "Domain 1 - Preventing people from dying prematurely",
    "Domain 2 - Enhancing quality of life for people with long-term conditions",
    "Domain 3 - Helping people to recover from ill-health or following injury",
    "Domain 4 - Ensuring people have a positive experience of care",
    "Domain 5 - Treating and caring for people in a safe environment and protecting them from avoidable harm",
]

raw_indicators = json.load(open('nhsof_indicators.json'))
work_done = json.load(open('nhsof_metadata_indicators.json'))

result = []
for i in work_done:
    i['frequency'] = ''
    i['status'] = 'Live'
    result.append(i)
done = len(work_done)
counter = done
print("Completed {}".format(done))
for indicator in raw_indicators:
    counter += 1
    print('{}/{}'.format(counter, len(raw_indicators)))
    print(indicator['title'])
    print('---------------------------------------------------')
    for field in fields:
        print(field)
        if field in indicator:
            print(indicator[field])
            answer = raw_input('Change? ').strip()
            if answer:
                value = raw_input('Value: ')
                indicator[field] = value.strip()
        else:
            value = raw_input('Value: ')
            indicator[field] = value.strip()
    indicator['language'] = 'en-GB'
    number = indicator['title'].split()[0]
    indicator['number'] = number
    indicator['status'] = 'Live'
    domain = domains[0]
    if number.startswith('2'):
        domain = domains[1]
    elif number.startswith('3'):
        domain = domains[2]
    elif number.startswith('4'):
        domain = domains[3]
    elif number.startswith('5'):
        domain = domains[4]
    indicator['domain'] = domain
    indicator['homepage'] = 'http://www.hscic.gov.uk/nhsof'
    indicator['description'] = """Definition
==========

{}

Specification
=============

Please see the "Indicator Specificiation", "DH Guidance for the NHS Outcomes Framework" and "Indicator Quality Statement" documents attached to this dataset as resource files listed below.""".format(indicator['definition'].encode('utf-8'))
    result.append(indicator)
    with open('nhsof_metadata_indicators.json', 'wb') as output:
        output.write(json.dumps(result, indent=2))
