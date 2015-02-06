# -*- codint: utf-8 -*-
#!/usr/bin/env python
"""
Scrape CCGOIS datasets from the complete list of indicators in the JSON file.
Then combine them with metadata extracted from the following document:

http://www.england.nhs.uk/wp-content/uploads/2013/12/ccg-ois-1415-tech-guid.pdf
"""
import json


# Generated via Eyeball Mk.1 Date ranges discovered by reading the XLS.
CCGOIS_INDICATORS = {
    "P01559": {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.1',
        'start_date': '2009-01-01',
        'end_date': '2013-12-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age and sex standardised potential years of life lost to conditions amenable to healthcare in the respective calendar year per 100,000 CCG population.

Clinical rationale
==================

Causes considered amenable to health care are those from which premature deaths should not occur in the presence of timely and effective health care. The concept of 'amenable' mortality generally relates to deaths under age 75, due to the difficulty in determining cause of death in older people who often have multiple morbidities. The Office for National Sta tistics (ONS) produces mortality data by cause, which excludes deaths under 28 days (for which cause of death is not classified by ICD - 10 codes). These indicators therefore relate to deaths between 28 days and 74 years of age inclusive.

ONS consulted on a proposed list of causes considered amenable to healthcare in February 2011 and updated the list in April 2012. ONS's definition and related data for 2010 for England and Wales can be found at:

http://www.ons.gov.uk/ons/rel/subnational-health4/avoidable-mortality-in-england-and-wales/2010/stb-avoidable-mortality.html

Data Source
===========

Primary Care Mortality Database (PCMD), provided by ONS.

ONS population estimates:

http://www.ons.gov.uk/ons/rel/pop-estimate/population-estimates-for-england-and-wales/index.html

GP registered population, National Health Application Infrastructure Services (NHAIS) ('Exeter') System.

Numerator
=========

Death registrations in the calendar year for all England deaths based on GP of registration from the Primary Care Mortality Database (PCMD).

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems, supplied annually on 1 January for the forthcoming calendar year.
        """,
        'nhs_of_indicators': '1a i and ii',
    },
    'P01560': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.2',
        'start_date': '2009-01-01',
        'end_date': '2013-12-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'nhs_of_indicators': '1.1',
        'description': """Definition
==========

Directly age and sex standardised mortality rate from cardiovascular disease for people aged under 75 in the respective calendar year per 100,000 CCG population.

Clinical rationale
==================

One of four improvement areas which account for the large portions of the disease burden amenable to health care. Progress in these outcomes therefore provides a useful initial analysis of what accounts for progress in the overarching indicators. This indicator measures premature mortality from cardiovascular disease, and seeks to encourage measures such as the prompt diagnosis and effective management of cardiovascular conditions and treatments to reduce the re-occurrence of cardiovascular disease events and to prevent or to slow the process of chronic cardiovascular conditions. The detection of risk factors for, and the diagnosis and effective treatment of, cardiovascular disease will influence mortality associated with cardiovascular disease.

Data source
===========

Primary Care Mortality Database (PCMD) provided by the Office for National Statistics

GP registered population, NHAIS (Exeter) System

Numerator
=========

Death registrations in the calendar year for all England deaths based on GP of registration from the Primary Care Mortality Database (PCMD)

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems, supplied annually on 1 January for the forthcoming calendar year.
""",
    },
    'P01561': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.6',
        'start_date': '2009-01-01',
        'end_date': '2013-12-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': '1.2',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age and sex standardised mortality rate from respiratory disease for people aged under 75 in the respective calendar year per 100,000 CCG population.

Clinical rationale
==================

One of four improvement areas which account for the large portions of the disease burden amenable to health care. Progress in these outcomes therefore provides a useful initial analysis of what accounts for progress in the overarching
indicators.

This indicator measures premature mortality from respiratory disease, and seeks to encourage measures such as early and accurate diagnosis, optimal pharmacotherapy, physical interventions, prompt access to specialist respiratory care, structured hospital admission and appropriate provision of home oxygen.

The detection of risk factors for, and the diagnosis and effective treatment of, respiratory disease will influence mortality associated with respiratory disease.

Data source
===========

Primary Care Mortality Database (PCMD) provided by the Office for National Statistics.

GP registered population, NHAIS (Exeter) System.

Numerator
=========

Death registrations in the calendar year for all England deaths based on GP of registration from the Primary Care Mortality Database (PCMD)

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems, supplied annually on 1 January for the forthcoming calendar year.
""",
    },
    'P01562': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.9',
        'start_date': '2009-01-01',
        'end_date': '2013-12-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': '1.4',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age and sex standardised mortality rate from cancer for people aged under 75 in the respective calendar year per 100,000 CCG population.

Clinical rationale
==================

One of four improvement areas which account for the large portions of the disease burden amenable to health care. Progress in these outcomes therefore provides a useful initial analysis of what accounts for progress in the overarching indicators.

This indicator measures premature mortality from cancer, and seeks to encourage measures such as early and accurate diagnosis, optimal pharmacotherapy, physical interventions, prompt access to specialist cancer care, structured hospital admission and appropriate provision of home oxygen.

Data source
===========

Primary Care Mortality Database (PCMD) provided by the Office for National Statistics.

GP registered population, NHAIS (Exeter) System.

Numerator
=========

Death registrations in the calendar year for all England deaths based on GP of registration from the Primary Care Mortality Database (PCMD)

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems; supplied annually on 1 January for the forthcoming calendar year.
""",
    },
    'P01565': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.8',
        'start_date': '2010-01-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Quarterly',
        'description': """Definition
==========

Directly age and sex standardised emergency admission rate for alcohol related liver disease in adults per 100,000 CCG population.

Clinical rationale
==================

Some, but not all admissions for liver disease may be potentially avoidable by high quality management in primary care. This indicator therefore acts as a proxy for overall management.

Data source
===========

Hospital Episode Statistics (HES)

GP registered population, NHAIS (Exeter) System

Numerator
=========

HES Continuous Inpatient Spells (CIPS). The CIP spells are constructed by the HSCIC HES Development team.

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems, supplied annually on 1 April for the forthcoming financial year.
"""
    },
    'P01609': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.7',
        'start_date': '2009-01-01',
        'end_date': '2013-12-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': '1.3',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age and sex standardised mortality rate from liver disease for people aged under 75 in the respective calendar year per 100,000 CCG population

Clinical rationale
==================

One of four improvement areas which account for the large portions of the disease burden amenable to health care. Progress in these outcomes therefore provides a useful initial analysis of what accounts for progress in the overarching indicators.

This indicator measures premature mortality from liver disease, and seeks to encourage measures such as prevention, early and accurate diagnosis and timely access to appropriate treatment and support.

Data source
===========

Primary Care Mortality Database (PCMD) provided by the Office for National Statistics

GP registered population, NHAIS (Exeter) System

Numerator
=========

Death registrations in the calendar year for all England deaths based on GP of registration from the Primary Care Mortality Database (PCMD)

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems, supplied annually on 1 January for the forthcoming calendar year.
"""
    },
    'P01664': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.4',
        'start_date': '2011-01-01',
        'end_date': '2012-12-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Annually',
        'description': """Definition
==========

Indirectly age and sex standardised rate for myocardial infarction, stroke and stage 5 chronic kidney disease per 100 people with diabetes in the National Diabetes Audit.

Clinical rationale
==================

The intent of this indicator is to measure the proportion of people with diabetes who develop long-term conditions or complications that may be exacerbated by poor management of diabetes. Some, but not all, complications or episodes of ill-health may potentially be avoidable with high-quality management of diabetes in primary care. These long-term conditions or complications are therefore used as proxies for outcomes of care.

Data source
===========

National Diabetes Audit (NDA)

GP practice to CCG mapping file from the HSCIC website:

http://systems.hscic.gov.uk/data/ods/datadownloads/gppractice

Numerator
=========

Number of people collected by the NDA who have HES primary or secondary diagnosis (ICD10) codes, or primary and secondary OPCS codes during the follow-up period of MI, stroke or end stage kidney disease.

Denominator
===========

Number of people with diabetes identified by the NDA who were alive at the start of the follow-up period.
""",
    },
    'P01665': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.14',
        'start_date': '2013-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Quarterly',
        'description': """Definition
==========

The percentage of women who were smokers at the time of delivery, out of the number of maternities.

Clinical rationale
==================

This indicator measures a key component of high-quality care as defin ed in NICE clinical guideline 62, recommendation 1.3.10.4, which states: "Monitor smoking status and offer smoking cessation advice, encouragement and support throughout the pregnancy and beyond".

Data source
===========

HSCIC Omnibus

http://www.hscic.gov.uk/datacollections/ssatod

Numerator
=========

Number of maternities where mother recorded as smoking at delivery

Denominator
===========

Number of maternities in the relevant CCG
"""
    },
    'P01677': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.10',
        'start_date': '1996-01-01',
        'end_date': '2012-12-31',
        'assurance_level': 'Not yet assured',
        'status': 'In development',
        'nhs_of_indicators': '1.4i',
        'frequency': 'Annually',
        'description': """Definition
==========

One-year standardised relative survival percentage for adults (15-99 years).

An aggregate indicator for one year survival for all cancers in adults 15+. Relative survival is an estimate of the probability of survival from the cancer alone. It is defined as the ratio of the observed survival and the survival that would have been expected if the cancer patients had experienced the same background mortality by age and sex as the general population.

Note: ONS may replace 'relative survival' with 'net survival'. 2011 figure will be on a different basis from the previous figures. See link to latest data using new methodology, which explains the difference:

http://www.ons.gov.uk/ons/rel/cancer-unit/cancer-survival/2006---2010--followed-up-to-2011/stb-cancer-survival.html

Clinical rationale
==================

Reduced years of life lost from cancer

Data source
===========

ONS: mortality data by cause (England and Wales):

http://www.ons.gov.uk/ons/rel/vsob1/mortality-statistics-deaths-registered-in-england-and-wales-series-dr-/2010/dr-table5-2010.xls

ONS: mid-year population estimates:

http://www.ons.gov.uk/ons/publications/re-reference-tables.html?edition=tcm%3A77-231847

and

http://www.ons.gov.uk/ons/rel/pop-estimate/population-estimates-for-england-and-wales/index.html

ONS: cancer registrations data:

http://www.ons.gov.uk/ons/rel/vsob1/cancer-statistics-registrations-england-series-mb1-/no-41-2010/rft-cancer-registrations-2010.xls

Calculation
===========

Calculated rates provided by the London School of Hygiene and Tropical Medicine
"""
    },
    'P01678': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.11',
        'start_date': '1996-01-01',
        'end_date': '2012-12-31',
        'assurance_level': 'Not yet assured',
        'status': 'In development',
        'nhs_of_indicators': '1.4.iii',
        'frequency': 'Annually',
        'description': """Definition
==========

One-year standardised relative survival percentage for adults (15-99 years).

An aggregate indicator for one year survival for all cancers in adults 15+. Relative survival is an estimate of the probability of survival from the cancer alone. It is defined as the ratio of the observed survival and the survival that would have been expected if the cancer patients had experienced the same background mortality by age and sex as the general population.

Colorectal, breast and lung cancers are defined in terms of the following ICD-10 codes: Colorectal C18-C20, C21.8; Breast C50; Lung C33-C34.

Note: ONS may replace 'relative survival' with 'net survival'. 2011 figure will be on a different basis from the previous figures. See link to latest data using new methodology, which explains the difference:

http: //www.ons.gov.uk/ons/rel/cancer-unit/cancer-survival/2006---2010--followed-up-to-2011/stb-cancer-survival.html

Clinical rationale
==================

Reduced years of life lost from cancer

Data source
===========

ONS: mortality data by cause (England and Wales):

http://www.ons.gov.uk/ons/rel/vsob1/mortality-statistics-deaths-registered-in-england-and-wales-series-dr-/2010/dr-table5-2010.xls

ONS: mid-year population estimates:

http://www.ons.gov.uk/ons/publications/re-reference-tables.html?edition=tcm%3A77-231847

and

http://www.ons.gov.uk/ons/rel/pop-estimate/population-estimates-for-england-and-wales/index.html

ONS: cancer registrations data:

http://www.ons.gov.uk/ons/rel/vsob1/cancer-statistics-registrations-england-series-mb1-/no-41-2010/rft-cancer-registrations-2010.xls

Calculation
===========

Calculated rates provided by the London School of Hygiene and Tropical Medicine
""",
    },
    'P01679': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.13',
        'start_date': '2013-04-01',
        'end_date': '2013-09-30',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Quarterly',
        'description': """Definition
==========

Number of women in the relevant CCG population who have seen a midwife or a maternity healthcare professional, for health and social care assessment of needs, risks and choices by 12 weeks and six days of pregnancy

Clinical rationale
==================

This indicator measures a key component of high-quality care as defined in Antenatal care NICE clinical guideline 62 (2008).

Recommendation 1.2.5.2 states: "Early in pregnancy, all women should receive appropriate written information about the likely number, timing and content of antenatal appointments associated with different options of care and be given an opportunity to discuss this schedule with their midwife or doctor".

Data source
===========

Unify2

Numerator
=========

Number of women in the relevant CCG population who have seen a midwife or a maternity healthcare professional for health and social care assessment of needs, risks and choices by 12 weeks and six days of pregnancy

Denominator
===========

Not applicable
""",
    },
    'P01680': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.15',
        'start_date': '2013-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Quarterly',
        'description': """Definition
==========

Breast feeding prevalence at 6-8 weeks

Clinical rationale
==================

This indicator measures an outcome of a key component of high-quality care as defined in NICE guideline 62, recommendation 1.1.1.1, which states: "New antenatal information should be given to pregnant women according to the following schedule. Before or at 36 weeks: breastfeeding information, including technique and good management practices that would help a woman succeed, such as detailed in the UNICEF 'Baby Friendly Initiative'."

Data Source
===========

Unify2

Numerator
=========

Number of infants totally or partially breastfed at 6-8 weeks of age

Denominator
===========

Number of infants whose breastfeeding status was known at 6-8 weeks
""",
    },
    'P01692': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.17',
        'start_date': '2012-01-01',
        'end_date': '2012-12-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Annually',
        'description': """Definition
==========

The percentage of new cases of cancer for which a valid stage is recorded, for a given year, given by CCG

Clinical rationale
==================

A major determinant of cancer outcomes is the tumour stage at diagnosis. Improving the recording of cancer stage at diagnosis will allow more detailed and actionable analyses of outcomes by treatment type, patient pathway, a nd case mix.

Data source
===========

Cancer Analysis System (CAS), National Cancer Intelligence Network (NCIN)

Numerator
=========

Of the cases of cancer in the denominator, the number with a valid stage at diagnosis recorded, as defined by the former United Kingdom Association of Cancer Registries (UKACR) registration rules

Denominator
===========

The number of new invasive cases of cancer (ICD-10 diagnosis codes are C00-C97), excluding non-melanoma skin cancer (C44), diagnosed during the respective year
""",
    },
    'P01693': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.18',
        'start_date': '2012-01-01',
        'end_date': '2012-12-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Annually',
        'description': """Definition
==========

The percentage of new cases of cancer which were diagnosed at stage 1 or 2 for the specific cancer sites, morphologies and behaviour: invasive malignancies of breast, prostate, colorectal, lung, bladder, kidney, ovary, uterus, non-Hodgkin lymphoma and invasive melanomas of skin, given by CCG

Clinical rationale
==================

Diagnosing cancer at an early stage improves the chance of survival. Specific public health interventions, such as screening programmes and information and education campaigns, aim to improve rates of early diagnosis. This indicator is therefore a useful proxy for assessing likely improvements in cancer survival rates.

Data source
===========

Cancer Analysis System (CAS), National Cancer Intelligence Network (NCIN).

Numerator
=========

Of cases of cancer in the denominator, the number diagnosed at stage 1 or 2

Denominator
===========

The number of new cases of cancer diagnosed during the respective year, at any stage or unknown stage, for the specific cancer sites, morphologies and behaviour: invasive malignancies of breast, prostate, colorectal, lung, bladder, kidney, ovary, uterus, non-Hodgkin lymphoma and invasive melanomas of skin
""",
    },
    'P01694': {
        'domain': "Domain 1 - Preventing People Dying Prematurely",
        'number': '1.20',
        'start_date': '2009-01-01',
        'end_date': '2013-12-31',
        'assurance_level': 'Assurance initiated',
        'status': 'In development',
        'nhs_of_indicators': 'Not applicable',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age standardised mortality rate from breast cancer for women, per 100,000 female CCG population

Clinical rationale
==================

Breast cancer is the most common cancer in women in England and also affects a very small proportion of men. There is a trend of increasing incidence because of lifestyle factors and improved detection, and decreasing mortality because of earlier detection and improvements in the quality and availability of effective treatments.

Data source
===========

Primary Care Mortality Database (PCMD) provided by the Office for National Statistics

GP registered population, NHAIS (Exeter) System

Numerator
=========

The number of registered deaths from breast cancer during the respective calendar year by CCG and 5-year age group, females, all ages.  Breast cancer is identified by ICD-10 code: C50.

Denominator
===========

CCG female population, by 5-year age group, from aggregated practice populations as at 1 January for the forthcoming calendar year
""",
    },
    'P01564': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.7',
        'start_date': '2010-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age and sex standardised rate of unplanned hospital admissions for asthma, diabetes and epilepsy in under 19s

Clinical rationale
==================

The intent of this indicator is to measure effective management and reduced serious deterioration in young people with specific long term conditions. Active management of these conditions can prevent acute exacerbations and reduce the need for emergency hospital admission.

Data source
===========

Hospital Episode Statistics (HES)

GP registered population, NHAIS (Exeter) System

Numerator
=========

Hospital Episode Statistics (HES) Continuous Inpatient Spells (CIPS). The CIP spells are constructed by the HSCIC HES Development team.

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems; extracted annually on 1 April for the forthcoming financial year
""",
        'nhs_of_indicators': '2.3ii',
    },
    'P01563': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.6',
        'start_date': '2010-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

Directly age and sex standardised rate of unplanned hospitalisation admissions for chronic ambulatory care sensitive conditions

Clinical rationale
==================

The intent of this indicator is to measure effective management and reduced serious deterioration in people with ACS conditions. Active management of ACS conditions such as COPD, diabetes, congestive heart fai lure and hypertension can prevent acute exacerbations and reduce the need for emergency hospital admission.

Data source
===========

Hospital Episode Statistics (HES)

GP registered population, NHAIS (Exeter) System

Numerator
=========

Hospital Episode Statistics (HES) Continuous Inpatient Spells (CIPS). The CIP spells are constructed by the HSCIC HES Development team.

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems; extracted annually on 1 April for the forthcoming financial year
""",
        'nhs_of_indicators': '2.3i',
    },
    'P01627': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.2',
        'start_date': '2011-07-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

Proportion of people feeling supported to manage their conditions, based on responses to one question from the GP Patient Survey

Clinical rationale
==================

Together with indicator 2.1, this improvement indicator should provide a picture of the NHS contribution to improving the quality of life for those with long-term conditions.

Data source
===========

GP Patient Survey

Numerator
=========

The weighted number of 'Yes, definitely' and 'Yes, to some extent' responses to question 32 of the GP Patient Survey multiplied by the non-response weight from the GP Patient survey (wt_new)

Denominator
===========

The total number of 'Yes, definitely', 'Yes, to some extent' and 'No' responses to question 32 multiplied by the non-response weight from the GP Patient Survey (wt_new)
""",
        'nhs_of_indicators': '2.1',
    },
    'P01662': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.15',
        'start_date': '2011-07-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

Average health status (EQ-5D*) scores for individuals aged 18 and over reporting that they are carers

Clinical rationale
==================

The health status of carers plays an important role in their ability to support the individuals for whom they provide care.

Data source
===========

GP Patient Survey (GPPS)

Numerator
=========

The sum of weighted EQ-5D scores for all responses from people who indicate that they are carers

Denominator
===========

The sum of weighted responses from people who indicate that they are carers. Where being a carer is defined by answering yes to question 56 in the GPPS.
""",
        'nhs_of_indicators': '1.4',
    },
    'P01663': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.1',
        'start_date': '2011-07-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

Average health status (EQ-5D*) scores for individuals aged 18 and over reporting that they have a long-term condition. It assesses whether health-related quality of life is increasing over time for the population with long-term conditions, while controlling for measurable confounders (age, gender, disease mix etc).

Clinical rationale
==================

The overarching indicator (together with complementary improvement indicators) provides a picture of the NHS contribution to improving the quality of life for those affected by long-term conditions.

Data source
===========

GP Patient Survey

Numerator
=========

The sum of the weighted EQ-5D values for all responses from people identified as having a long-term condition

Denominator
===========

The sum of all weighted responses from people identified as having a long-term condition
""",
        'nhs_of_indicators': '2.0',
    },
    'P01666': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.5',
        'start_date': '2011-04-01',
        'end_date': '2012-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

The percentage of people with diabetes diagnosed less than a year who are referred to structured education

Clinical rationale
==================

This indicator measures a key component of high-quality care as defined in the NICE quality standard for diabetes, Statement 1: "People with diabetes and/or their carers receive a structured educational programme that fulfils the nationally agreed criteria from the time of diagnosis, with annual review and access to ongoing education".

Data source
===========

National Diabetes Audit

Numerator
=========

The number of people who were offered structured education during the following 12 months. For example, for those diagnosed in 2012, the number of people who were offered structured education in 2012/13

Denominator
===========

People with diabetes who were newly diagnosed with diabetes during audit period, for example those diagnosed in 2012
""",
        'nhs_of_indicators': 'Not applicable',
    },
    'P01667': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.8',
        'start_date': '2011-04-01',
        'end_date': '2012-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

Indirectly age and sex standardised rate per 100 for complications associated with diabetes

Clinical rationale
==================

Some complications associated with diabetes are avoidable with high-quality diabetes management in primary care. Rates of lower limb amputation are therefore used as a proxy for outcomes of care.

This indicator also relates to a key component of high-quality care as defined in the NICE quality standard for diabetes: Statement 10: "People with diabetes with or at risk of foot ulceration receive regular review by a foot protection team in accordance with NICE guidance, and those with a foot problem requiring urgent medical attention are referred to and treated by a multidisciplinary foot care team within 24 hours".

Data source
===========

National Diabetes Audit (NDA)

Numerator
=========

Number of people identified by NDA in the denominator with a HES record of NDA complications using ICD-10 primary or secondary diagnosis codes, or primary and secondary OPCS codes

Denominator
===========

Number of people with diabetes identified by the NDA who were alive at the start of the follow-up period
""",
        'nhs_of_indicators': 'Not applicable',
    },
    'P01668': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.9',
        'start_date': '2013-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

Access to community mental health services by BME groups

Clinical rationale
==================

This indicator reflects access to mental health services among people from black and minority ethnic groups. Service user experience in adult mental health (NICE clinical guideline 136, 2011), recommendation 1.2.5, states: "Local mental health services should work with primary care and local third sector, including voluntary, organisations to ensure that: all people with mental health problems have equal access to services based on clinical need and irrespective of gender, sexual orientation, socioeconomic status, age, background (including cultural, ethnic and religious background) or disability and that services are culturally appropriate".

Data source
===========

Mental Health Minimum Data Set (MHMDS)

ONS mid-year population estimates

Numerator
=========

The number of people using adult and elderly NHS secondary mental health services by ethnic group and ethnic subgroup.

Denominator
===========

The total number of people by ethnic group using Office for National Statistics (ONS) Population Estimates from the 2011 Census for England by ethnic group and subgroup.
""",
        'nhs_of_indicators': 'Not applicable',
    },
    'P01681': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.10',
        'start_date': '2012-04-01',
        'end_date': '2013-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

Access to psychological therapy services by people from black and minority ethnic groups

Clinical rationale
==================

The Improving Access to Psychological Therapies (IAPT) programme develops talking therapies services that offer treatments for depression and anxiety disorders approved by NICE. A major ambition of the programme is to ensure equity of access in line with both prevalence and the community profile including age, race and other protected quality characteristics described in the Equality Act 2010.

Data source
===========

IAPT data set.

ONS mid-year population estimates

Numerator
=========

The number of people using talking therapies by ethnic group

Denominator
===========

The total number of people by ethnic group using Office for National Statistics (ONS) Population Estimates from the 2011 Census for England by ethnic group and subgroup.
""",
        'nhs_of_indicators': 'Not applicable',
    },
    'P01695': {
        'domain': "Domain 2 - Enhanced Quality of Life for People with Long-Term Conditions",
        'number': '2.16',
        'start_date': '2013-07-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assurance initiated',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

The average weighted health status (EQ-5D) score for adults with a long-term mental health condition, given by CCG

Clinical rationale
==================

The indicator supports identification of the degree to which wider health needs of individuals with a long-term mental health condition are being addressed.

Data source
===========

GP Patient Survey

Numerator
=========

The sum of weighted EQ-5D scores for all responses from people who identify themselves as having a long-term mental health condition

Denominator
===========

The sum of all weighted responses from people who identify themselves as having a long-term mental health condition
""",
        'nhs_of_indicators': 'Not applicable',
    },
    'P01566': {
        'domain': "Domain 3 - Helping people to recover from episodes of ill health or following injury",
        'number': '3.1',
        'start_date': '2011-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Quarterly',
        'description': """Definition
==========

Directly age and sex standardised rate of emergency admissions for acute conditions that should not usually require hospital admission

Clinical rationale
==================

Preventing conditions such as ear, nose or throat infections, kidney or urinary tract infections, or heart failure from becoming more serious. Some emergency admissions may be avoided for acute conditions that are usually managed in primary care. Rates of emergency admissions are therefore used as a proxy for outcomes of care.

Data source
===========

Hospital Episode Statistics (HES)

GP registered population, NHAIS (Exeter) System

Numerator
=========

The number of finished and unfinished continuous inpatient spells (CIPS), excluding transfers, with an emergency method of admission and with primary diagnoses for acute conditions that should not usually require hospital admission

Denominator
===========

CCG level count of patients registered with the constituent GP practices
""",
        'nhs_of_indicators': '3a',
    },
    'P01567': {
        'domain': "Domain 3 - Helping people to recover from episodes of ill health or following injury",
        'number': '3.2',
        'start_date': '2010-04-01',
        'end_date': '2012-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Quarterly',
        'description': """Definition
==========

Percentage of emergency admissions to any hospital in England occurring within 30 days of the last, previous discharge from hospital after admission; indirectly standardised by age, sex, method of admission and diagnosis / procedure. Admissions for cancer and obstetrics are excluded.

Clinical rationale
==================

Effective recovery from illnesses and injuries requiring hospitalisation. Some emergency re-admissions within a defined period after discharge from hospital result from potentially avoidable adverse events, such as incomplete recovery or complications. Emergency re-admissions are therefore used as a proxy for outcomes of care.

Data source
===========

Hospital Episode Statistics (HES)

GP registered population, NHAIS (Exeter) System

Numerator
=========

The number of finished and unfinished continuous inpatient spells (CIPS) that are emergency admissions within 0-29 days (inclusive) of the last, previous discharge from hospital (see denominator), including those where the patient dies, but excluding the following: those with a main specialty upon readmission coded under obstetric and those where the readmitting spell has a diagnosis of cancer (other than benign or in situ) or chemotherapy for cancer coded anywhere in the spell.

The date of the last, previous discharge from hospital, and the date and method of admission from the following CIP spell, are used to determine the interval between discharge and emergency readmission.

The numerator is based on a pair of spells, the discharge spell and the next subsequent readmission spell (this spell must meet the numerator criteria). The selection process thus carries over the characteristics of the denominator for the discharge spell and applies additional ones to the readmission spell.

Denominator
===========

The number of finished CIP spells within selected medical and surgical specialties, with a discharge date up to 31 March within the year of analysis. Day cases, spells with a discharge coded as death, maternity spells (based on specialty, episode type, diagnosis), and those with mention of a diagnosis of cancer or chemotherapy for cancer anywhere in the spell are excluded. Patients with mention of a diagnosis of cancer or chemotherapy for cancer anywhere in the 365 days prior to admission are excluded.
""",
        'nhs_of_indicators': '3b',
    },
    'P01568': {
        'domain': "Domain 3 - Helping people to recover from episodes of ill health or following injury",
        'number': '3.3',
        'start_date': '2010-04-01',
        'end_date': '2013-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

Patient's reported improvement in health status following elective procedures: currently, hip replacement, knee replacement, groin hernia and varicose veins. The Patient Reported Outcome Measures (PROMs) indicators are reported separately for the four separate conditions.

The questionnaires provided to patients measure their health status before the procedure and 3-6 months after (depending on the procedure). A comparison of these measurements shows whether, and to what extent, the procedure has improved their health status.

Clinical rationale
==================

Measuring health gain as assessed by patients for planned treatments.

Data source
===========

PROMs dataset, the Health and Social Care Information Centre (HSCIC).

Calculation
===========

The value is sourced fully calculated.

PROMs comprise a pair of questionnaires completed by the patient, one before and one after surgery (at least three months after for groin hernia and varicose vein operations, or at least six months after for hip and knee replacements). Patients' self-reported health status (sometimes referred to as health related quality of life) is assessed through a mixture of generic and disease or condition-specific questions. To add to the value of the PROMs questionnaire data, it is linked routinely with HES episode-level information.

A list of all of the items in the PROMs dataset is included in the PROMS Data Dictionary and the PROMs website provides a guide to methodology. Both can be accessed via:

http://www.hscic.gov.uk/proms
""",
        'nhs_of_indicators': '3.1 i-iv',
    },
    'P01569': {
        'domain': "Domain 3 - Helping people to recover from episodes of ill health or following injury",
        'number': '3.4',
        'start_date': '2010-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Quarterly',
        'description': """Definition
==========

Directly age and sex standardised rate of children under 19 (0 to 18 years) admitted to hospital with lower respiratory tract infections as an emergency admission during the respective financial year. per 100,000 CCG population

Clinical rationale
==================

Preventing lower respiratory tract infections (LRTIs) in children from becoming more serious, for example, by preventing complications in vulnerable children and improving the management of conditions in the community, whilst taking into account that some children's conditions and cases might require an emergency hospital admission as part of current good clinical practice. For example, a clinical guideline for bronchiolitis published in November 2006 [1] recommends that children showing low oxygen saturation as measured by pulse oxymetry should be admitted to inpatient care.

[1] SIGN - Scottish Intercollegiate Guidelines Network (November 2006). Guideline 91. Bronchiolitis in Children - a national clinical guideline:

http://www.sign.ac.uk/guidelines/fulltext/91/index.htm

Data source
===========

HES Continuous Inpatient Spells (CIPS).

GP registered population, NHAIS (Exeter) System

Numerator
=========

The number of finished and unfinished continuous inpatient spells (CIPS), excludi ng transfers, for children with an emergency method of admission and with primary diagnoses for lower respiratory tract infections

Denominator
===========

Unconstrained GP registered population counts by single year of age and sex from the NHAIS (Exeter) Systems; supplied annually on 1 April for the forthcoming financial year
""",
        'nhs_of_indicators': '3.2',
    },
    'P01570': {
        'domain': "Domain 4 - Ensuring that people have a positive experience of care",
        'number': '4.1',
        'start_date': '2011-07-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

Patient experience of GP out-of-hours services, measured by scoring the results of one question from the GP Patient Survey (GPPS)

The indicator is based on the percentage of people responding 'Good' or 'Very Good' to the following question: 'Overall, how would you describe your experience of out-of-hours GP services?'

Clinical rationale
==================

Improvement in patients' experiences of GP out-of-hours services

Data source
===========

GP Patient Survey

Numerator
=========

Number of people answering 'Very Good' or 'Good' to the question above

Denominator
===========

The total number of people answering the question above
""",
        'nhs_of_indicators': '4a ii',
    },
    'P01696': {
        'domain': "Domain 4 - Ensuring that people have a positive experience of care",
        'number': '4.2',
        'start_date': '2013-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Annually',
        'description': """Definition
==========

This Overall Patient Experience score is the average (mean) of five domain scores, and each domain score is the average (mean) of scores from a number of selected questions in the CQC Inpatient Services Survey

Clinical rationale
==================

Improvement in patients' experiences of NHS inpatient care

Data source
===========

The Care Quality Commission's Adult Inpatient Survey - from the CQC nationally coordinated patient survey programme.

The latest Adult Inpatient Survey (2012) was published by CQC at:

http://www.cqc.org.uk/aboutcqc/howwedoit/involvingpeoplewhouseservices/patientsurveys/inpatientservices.cfm

Results for the updated Overall Patient Experience measure, as used for this indicator, are published by DH at:

http://transparency.dh.gov.uk/tools-for-understanding-patient-experience/

Guidance material for this survey (covering inclusion and exclusion criteria for compiling the sample frame) is available on the NHS national patient survey coordination centre website:

http://www.nhssurveys.org
""",
        'nhs_of_indicators': '4b',
    },
    'P01697': {
        'domain': "Domain 4 - Ensuring that people have a positive experience of care",
        'number': '4.5',
        'start_date': '2013-04-01',
        'end_date': '2014-03-31',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Annually',
        'description': """Definition
==========

The indicator is a composite, calculated as the average of five survey questions. Each question describes a different element of the overarching theme 'responsiveness to patients' personal needs'.

Clinical rationale
==================

Improvement in responsiveness to patients' inpatient care needs.

Data source
===========

The Care Quality Commission's Adult Inpatient Survey - from the CQC natio nally coordinated patient survey programme.

The latest Adult Inpatient Survey (2012) was published in April 2013 at:

http://www.cqc.org.uk/public/reports-surveys-and-reviews/surveys/inpatient-survey-2011

Guidance material for this survey (covering inclusion and exclusion criteria for compiling the sample frame) is available on the NHS national patient survey coordination centre website:

http://www.nhssurveys.org
""",
        'nhs_of_indicators': '4.2',
    },
    'P01628': {
        'domain': "Domain 5 - Treating and Caring for People in a Safe Environment and Protecting Them From Avoidable Harm",
        'number': '5.3',
        'start_date': '2013-04-01',
        'end_date': '2014-06-30',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Quarterly',
        'description': """Definition
==========

The number of MRSA bloodstream infections reported per CCG

Clinical rationale
==================

Reducing the incidence of healthcare associated infections (HCAI)

Data source
===========

Mandatory surveillance by Public Health England (PHE)

http://www.hpa.org.uk/web/HPAweb&HPAwebStandard/HPAweb_C/1254510675444

Numerator
=========

The number of MRSA bloodstream infections

Denominator
===========

Not applicable
""",
        'nhs_of_indicators': '5.2 i',
    },
    'P01698': {
        'domain': "Domain 5 - Treating and Caring for People in a Safe Environment and Protecting Them From Avoidable Harm",
        'number': '5.1',
        'start_date': '2013-04-01',
        'end_date': '2014-06-30',
        'assurance_level': 'Assured',
        'status': 'In development',
        'frequency': 'Quarterly',
        'description': """Definition
==========

For each of a CCG's five main providers, this indicator shows the rate of patient safety incidents per 1,000 total provider bed days

Clinical rationale
==================

Improved readiness of the NHS to report harm and to learn from it.

Reporting patient safety incidents and identifying common risks to patients should increase awareness and provide opportunities to improve patient safety.

Data source
===========

Organisation Patient Safety Incident workbook, reported to the National Patient Safety Agency (NPSA) by the National Reporting and Learning System (NRLS)

HES Admitted Patient Care (APC) data

Numerator
=========

For each CCG this indicator will report the number of patient safety incidents as reported by their five main providers alongside a rate of patient safety incidents per 1,000 total provider bed days.

The five main providers are the ones that a CCG commissions most activity with. All of the figures are reported at provider level.

Denominator
===========

Not applicable
""",
        'nhs_of_indicators': '5a',
    },
    'P01629': {
        'domain': "Domain 5 - Treating and Caring for People in a Safe Environment and Protecting Them From Avoidable Harm",
        'number': '5.4',
        'start_date': '2013-04-01',
        'end_date': '2013-09-30',
        'assurance_level': 'Assured',
        'status': 'Live',
        'frequency': 'Quarterly',
        'description': """Definition
==========

The number of C. difficile infections reported, in people aged 2 and over, per CCG.

Clinical rationale
==================

Reducing the incidence of healthcare associated infections (HCAI)

Data source
===========

Mandatory surveillance by Public Health England

http://www.hpa.org.uk/web/HPAweb&HPAwebStandard/HPAweb_C/1254510678961

Numerator
=========

The number of C. difficile infections reported, in people aged two and over

Denominator
===========

Not applicable
""",
        'nhs_of_indicators': '5.2 ii',
    },
}

import os

def get_metadata_file(filename):
    root = os.path.dirname(__file__)
    f = os.path.join(root, os.path.pardir, os.path.pardir, "metadata", filename)
    return os.path.abspath(f)

def main(workspace):
    all_indicators = json.load(open(get_metadata_file('data/indicators.json')))
    ccgois_indicators = []
    found = []
    for indicator in all_indicators:
        id = indicator['unique identifier']
        if id in CCGOIS_INDICATORS:
            print id
            # Found one!
            ccgi = CCGOIS_INDICATORS[id]
            found.append(id)
            indicator['domain'] = ccgi['domain']
            indicator['number'] = ccgi['number']
            indicator['coverage_start_date'] = ccgi['start_date']
            indicator['coverage_end_date'] = ccgi['end_date']
            indicator['description'] = ccgi['description'] + "\n\nSource: http://www.england.nhs.uk/wp-content/uploads/2013/12/ccg-ois-1415-tech-guid.pdf."
            indicator['frequency'] = ccgi['frequency']
            indicator['homepage'] = 'http://www.hscic.gov.uk/article/2021/Website-Search?productid=14879&q=CCGOIS'
            indicator['nhs_of_indicators'] = ccgi['nhs_of_indicators']
            indicator['assurance_level'] = ccgi['assurance_level']
            indicator['status'] = ccgi['status']
            indicator['language'] = 'en-GB'
            ccgois_indicators.append(indicator)
    for k in CCGOIS_INDICATORS:
        if k not in found:
            raise ValueError('{} not found')
    json.dump(ccgois_indicators, open('ccgois_indicators.json', 'wb'), indent=2)

if __name__ == '__main__':
    main(None)