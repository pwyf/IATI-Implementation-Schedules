## Common Standard implementation schedule version of structure.py

identification = {
    'name': "Common Standard Implementation Schedule",
    'code': 'commonstandard3'
}

# Which sheets information can be found in
structure = {
    # Take this metadata from the agency page, because it includes the organisation ID
    'metadata': 4,
    'publishing': 2,
    'organisation': 3,
    'activity': 4
}

metadata = {
    'name' : {
        'row': 6,
        'col': 3
    },
    'code': {
        'row' : 6,
        'col' : 5
    },
    # This is actually missing from the CS templates, so just use an empty column
    'version': {
        'row' : 9,
        'col' : 3
    },
    'date': {
        'row' : 8,
        'col' : 3,
        'format': "%d/%m/%Y"
    }
}

# This file contains the mapping between the Implementation Schedule
# spreadsheets and the outputted XML files.

# Map of each column of the activity and organisation tables
header = ['','','','', 'status', 'publication-date', 'notes']

header_docs = ['', '', '', '','Status', 'Publication Date', 'Notes']

# Map each row in the organisation table to a named XML element
organisation_rows = ['','','','','','','', '','','','','','','','','','','total-budget', 'recipient-org-budget', 'recipient-country-budget', 'document-link'] 

# Documentation for each of these elements
organisation_docs = ['','','','','','','', '','','','','','','','','','','Annual forward planning budget data for agency', 'Annual forward planning budget for funded institutions', 'Annual forward planning budget data for countries', 'Organisation documents']


# Map each row in the activity table to a named XML element
# Either elementname, or (elementname, UNUSED, type)
# Where type is the value that the type attribute will have
activity_rows = [
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '', #16 rows
    '', #Identification',
    'reporting-org',
    'iati-identifier',
    'other-identifier',
    '', #Basic Activity Information',
    ('title', 'lang', 'agency'),
    ('title', 'lang', 'recipient' ),
    ('description', 'lang', 'agency'),
    ('description', 'lang', 'recipient'),
    'activity-status',
    ('activity-date', 'type', 'start'),
    ('activity-date', 'type', 'end'),
    'contact-info',
    ('participating-org', 'role', 'funding'),
    ('participating-org', 'role', 'extending'),
    ('participating-org', 'role', 'implementing'),
    ('participating-org', 'role', 'accountable'),
    '', #Geopolitical Information',
    'recipient-country',
    'recipient-region',
    'location',
    '', #Classifications',
    ('sector', 'type', 'crs'), # TODO Bring these terms in line with those used in the main XML
    ('sector', 'type', 'agency'),
    'policy-marker',
    'collaboration-type',
    'default-flow-type',
    'default-finance-type',
    'default-aid-type',
    'default-tied-status',
    '', #Financial',
    'budget',
    'planned-disbursement',
    ('budget-identifier', 'type', 'economic'),
    ('budget-identifier', 'type', 'administrative-functional'),
    '', #Financial Transaction',
    ('transaction', 'type', 'commitment'),
    ('transaction', 'type', 'disbursement'),
    ('transaction', 'type', 'reimbursement'),
    ('transaction', 'type', 'incoming'),
    ('transaction', 'type', 'repayment'),
    '', #Related Documents',
    'document-link',
    'activity-website',
    'related-activity',
    '', #Performance',
    ('conditions', 'info', 'attached'),
    ('conditions', 'info', 'text'),
    'result'
]

# Documentation for each of the activity rows
activity_docs = [
    '', 'Part IIIb - Activity data', '', 'Separate sheet to be completed by each agency that does/will publish data to the common standard', '', '', 'Organisation or Agency Name:', '', 'Date', '', '', """This tab refers to the availability of information at activity level. For each information item in the table, please make a general assessment of your agency's ability to provide the requested information on all your activities. For details of the code values for an item refer to the codes lists in Part IV.  

In the status column you can specify the degree of compliance for each information item. For instance, if you can provide the requested information on most of your projects or programmes, you can indicate this by selecting "Fully Compliant", if only for some projects or programmes you can select "Partially Compliant" with an explanation in the notes column.  

Note that the common standard uses the term 'activity' to describe the reported unit for all types of development co-operation resources. An activity is any project, programme, contract, cooperative agreement or financial arrangement that is reported at a level of detail that is meaningful to the recipient and manageable by the donor.""", 'Overlapping fields', 'Partially overlapping fields', '' 'Information Item', 'Identification', 'Reporting Organisation', 'IATI activity identifier', 'Other activity identifiers', 'Basic Activity Information', 'Activity Title (Agency language)', 'Activity Title (Recipient language)', 'Activity Description (Agency language)', 'Activity Description (Recipient language)', 'Activity Status', 'Activity Dates (Start Date)', 'Activity Dates (End Date)', 'Activity Contacts', 'Participating Organisation (Funding)', 'Participating Organisation (Extending)', 'Participating Organisation (Implementing)', 'Participating Organisation (Accountable)', 'Geopolitical Information', 'Recipient Country', 'Recipient Region', 'Sub-national Geographic Location', 'Classifications', 'Sector (DAC CRS)', 'Sector (Agency specific)', 'Policy Markers', 'Collaboration Type', 'Default Flow Type', 'Default Finance Type', 'Default Aid Type', 'Default Tied Aid Status', 'Financial', 'Activity Budget', 'Planned Disbursements', 'Budget identifier - Economic Classification (Capital/Recurrent)', 'Budget identifier - Administrative/Functional budget classification', 'Financial Transaction', 'Financial transaction (Commitment)', 'Financial transaction (Disbursement & Expenditure)', 'Financial transaction (Reimbursement)', 'Financial transaction (Incoming Funds)', 'Financial transaction (Loan repayment / interest repayment)', 'Related Documents', 'Activity Documents', 'Activity Website', 'Related Activity', 'Performance', 'Conditions attached Y/N', 'Text of Conditions', 'Results data'
]


# Map each row in the publishing table to an element
# And each cell to an attribute or narrative element
# () for unparsed rows, organisations
# ('', 'element for row', 'attribute/narrative', 'attribute/narrative', 'attribute/narrative')
publishing_rows = [
    # first attribute says which column   to start collecting data from
    # number of rows -1 = number of spreadsheet row.
    (), #1
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #10
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #20
    (),
    (),
    (),
    (),
    (),
    (),
    (2, 'thresholds', '', ''), 
    (),
    (),
    (2, 'exclusions', '', ''), #30
    (),
    (),
    (),
    (),
    (),
    ('split-scope', 'scope', {'current': {'col': 2}, 'future': {'row': 7, 'col': 2}}), #row 35 in reality
    (),
    (),
    (),
    (), #40
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #50
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #60
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #70
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #80
    (),
    # Common Standard schedules are not formatted the same as IATI schedules, so need to look for information 
    # across several rows. "split" allows you to do this. First option should be in the same row as the 
    # point in this publishing row (-1); second option should be 'row':N rows below. So the below should
    # start at row 82.
    (),
    (),
    (),
    (),
    ('split', 'publication-frequency', {'frequency': {'col': 3, 'opts': {0: 'Monthly', 1: 'Quarterly', 2: 'Annually'}}, 'timeliness': {'row': 4, 'col': 2, 'opts': {0: '1 month in arrears', 1: '1 quarter in arrears', 2: '1 year in arrears'}}}),
    (),
    (),
    (),
    (), #90
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #100
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #110
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #120
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #130
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #140
    ('split-pub','publication-timetable', 'date-initial'), # row 140 in reality
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (), #150
    ('split', 'license', {'license': {'col': 2, 'opts': {0: 'Public domain', 3: 'Attribution-only'}}}), # row 151 in reality
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
]

# Documentation for each of the publishing rows
# Note that these tuples are misaligned by 1 value from those above
publishing_docs = [
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
]


# List of XML elements that will contain a date
date_tags = [ 'publication-date', 'date-initial', 'date-full' ]
# List of XML elements that will contain a decimal value
decimal_tags = [ 'value' ]


# Codes for xml elements named in `header` above
#   ('activity' here is actually misleading, as it is used for both
#   activity and organisation elements)
codes_activity = {
    # Status
    'status': {     'Fully Compliant': 'fc',
                   'Fully compliant': 'fc',
                   'Fully compliant\n': 'fc',
                   'Future publication': 'fp',
                   'Partially compliant': 'pc',
                   'Partially Compliant': 'pc',
                   'Not publishing now': 'up',
                   'Not publishing now\n': 'up',
                   'Unable to publish': 'up',
                   'Under consideration': 'uc',
                   'Not applicable': 'na' },
    # Exclusions
    'exclusions': { 'a) Not applicable to organisation': 'a',
                    'b) A non-disclosure policy': 'b',
                    'c) Not currently captured and prohibitive cost': 'c',
                    'd) Other': 'd', 
                    'n/a (No exclusions)': '' }
}

# Codes for xml elements corresponding to an element from the publishing
# table.
# These were extracted from a hidden row in the excel spreadsheet
# Those named UNUSED and UNUSED2 were found here, but not used in any of
# the main tables.
codes = {   
    # Data quality
    'quality': {   'Unverified': 'u', 'Verified': 'v'},
    # Frequency
    'frequency': {   'Annually': 'a',
                     'Bi-annually': 'b',
                     'Fortnightly': 'f',
                     'Monthly': 'm',
                     'Other': 'o',
                     'Quarterly': 'q',
                     'Real time': 'r',
                     'Weekly': 'w'},
    # License type
    'license': {    'Attribution-only': 'a',
                    'Other (non-compliant)': 'o',
                    'Public domain': 'p'},
    # Lifecyle
    'point': {   'Implementation': 'i',
                 'Other': 'o',
                 'Pipeline/identification': 'p'},
    # Multi-level reporting
    'yesno': {   'No': 'n', 'Yes': 'y'},
    # Multi-level type
    'UNUSED': { 'Both': 'b',
                'Hierarchy': 'h',
                'Related activities': 'r'},
    # Segmentation
    'segmentation': {   'By country / region': 'b',
                        'Other': 'o',
                        'Single file': 's'},
    # Staff resource
    'UNUSED2': {  'Ad hoc': 'a',
                  'Dedicated resource': 'd',
                  'Other': 'o',
                  'Working group': 'w'},
    # System resource
    'resource': {  'Direct feed from internal systems': 'd',
                   'Excel spreadsheet conversion': 'e',
                   'Manual capture through an online tool (web entry platform)': 'm',
                   'Other': 'o'},
    # Timeliness
    'timeliness': {   '1 month in arrears': '1m',
                      '1 quarter in arrears': '1q',
                      '1 week in arrears': '1w',
                      '2 months in arrears': '2m',
                      '2 weeks in arrears': '2w',
                      '> 1 quarter in arrears': 'gt',
                      '1 year in arrears': 'gt',
                      'Other': 'o',
                      'Real time': 'r'},
    # User interface
    'status': {   'In development': 'i',
                  'No': 'n',
                  'Under consideration': 'u',
                  'Yes': 'y'}}

