import collections

publishers = [
    {
    "name": "Australia",
    "code": "AU"
    },
    {
    "name": "Austria",
    "code": "AT"
    },
    {
    "name": "Belgium",
    "code": "BE"
    },
    {
    "name": "Canada",
    "code": "CA"
    },
    {
    "name": "Denmark",
    "code": "DK"
    },
    {
    "name": "EU Institutions",
    "code": "EU"
    },
    {
    "name": "Finland",
    "code": "FI"
    },
    {
    "name": "France AFD",
    "code": "FR-3"
    },
    {
    "name": "France MAE",
    "code": "FR-6"
    },
    {
    "name": "Germany",
    "code": "DE"
    },
    {
    "name": "Greece",
    "code": "GR"
    },
    {
    "name": "Ireland",
    "code": "IE"
    },
    {
    "name": "Italy",
    "code": "IT"
    },
    {
    "name": "Japan",
    "code": "JP"
    },
    {
    "name": "Korea",
    "code": "KR"
    },
    {
    "name": "Luxembourg",
    "code": "LU"
    },
    {
    "name": "Netherlands",
    "code": "NL"
    },
    {
    "name": "New Zealand",
    "code": "NZ"
    },
    {
    "name": "Norway",
    "code": "NO"
    },
    {
    "name": "Portugal",
    "code": "PT"
    },
    {
    "name": "Spain",
    "code": "ES"
    },
    {
    "name": "Sweden",
    "code": "SE"
    },
    {
    "name": "Switzerland",
    "code": "CH"
    },
    {
    "name": "United Kingdom, DFID",
    "code": "GB-1"
    },
    {
    "name": "United States",
    "code": "US"
    },
    {
    "name": "African Development Bank",
    "code": "46002"
    },
    {
    "name": "Asian Development Bank",
    "code": "46004"
    },
    {
    "name": "GAVI Alliance",
    "code": "47122"
    },
    {
    "name": "Global Fund to Fight Aids, Tuberculosis and Malaria",
    "code": "47045"
    },
    {
    "name": "Inter-American Development Bank ",
    "code": "46012"
    },
    {
    "name": "International Fund for Agricultural Development (IFAD)",
    "code": "41108"
    },
    {
    "name": "World Bank",
    "code": "44000"
    },
    {
    "name": "Czech Republic",
    "code": "CZ"
    },
    {
    "name": "Hungary",
    "code": "HU"
    },
    {
    "name": "Iceland",
    "code": "IS"
    },
    {
    "name": "Israel",
    "code": "IL"
    },
    {
    "name": "Poland",
    "code": "PL"
    },
    {
    "name": "Slovak Republic",
    "code": "SK"
    },
    {
    "name": "Slovenia",
    "code": "SI"
    },
    {
    "name": "Turkey",
    "code": "TR"
    },
    {
    "name": "United Nations Development Group (UNDG)",
    "code": "UNDG"
    },
    {
    "name": "UN-CDF",
    "code": "41111"
    },
    {
    "name": "UN-DESA",
    "code": "UNDESA"
    },
    {
    "name": "UNDP",
    "code": "41114"
    },
    {
    "name": "UNFPA",
    "code": "41119"
    },
    {
    "name": "UN-Habitat",
    "code": "41120"
    },
    {
    "name": "UNICEF",
    "code": "41122"
    },
    {
    "name": "UNOPS",
    "code": "41AAA"
    },
    {
    "name": "UN-WOMEN",
    "code": "41124"
    },
    {
    "name": "WFP",
    "code": "41140"
    },
    {
    "name": "ILO",
    "code": "41302"
    }
]

elementgroups = collections.OrderedDict({
            'org': {
                'description': 'Organisation level',
                'order': 1
            },
            'identification': {
                'description': 'Identification',
                'order': 2
            },
            'basic-activity-information': {
                'description': 'Basic activity information',
                'order': 2
            },
            'geopolitical-information': {
                'description': 'Geopolitical information',
                'order': 3
            },
            'classifications': {
                'description': 'Classifications',
                'order': 4
            },
            'financial': {
                'description': 'Financial',
                'order': 5
            },
            'financial-transaction': {
                'description': 'Financial transaction',
                'order': 6
            },
            'related-documents': {
                'description': 'Related documents',
                'order': 7
            },
            'performance': {
                'description': 'Performance',
                'order': 8
            }
})

elements = collections.OrderedDict({
        'organisation': collections.OrderedDict({
            'total-budget': {
                'description': 'Organisation budget',
                'group': 'org',
                'order': 1
            },
            'recipient-org-budget': {
                'description': 'Funded institution budgets',
                'group': 'org',
                'order': 2
            }, 
            'recipient-country-budget': {
                'description': 'Recipient country budgets',
                'group': 'org',
                'order': 3
            },
            'document-link': {
                'description': 'Organisation documents',
                'group': 'org',
                'order': 4
            }
        }),
        'activity': collections.OrderedDict({
            'reporting-org': { 
                'description': 'Reporting organisation',
                'group': 'identification',
                'order': 5
            }, 
            'iati-identifier': { 
                'description': 'IATI Identifier',
                'group': 'identification',
                'order': 6
            }, 
            'other-identifier': { 
                'description': 'Other Identifier',
                'group': 'identification',
                'order': 7
            },
            'title': { 
                'description': 'Title',
                'defining_attribute': 'type', 
                'defining_attribute_values': {
                    'agency': {
                        'order': 1,
                        'description': 'Agency language'
                    },
                    'recipient': {
                        'order': 2,
                        'description': 'Recipient language'
                    }
                },
                'order': 8,
                'group': 'basic-activity-information'
            }, 
            'description': { 
                'description': 'Description',
                'defining_attribute': 'type', 
                'defining_attribute_values': {
                    'agency': {
                        'order': 1,
                        'description': 'Agency language'
                    },
                    'recipient': {
                        'order': 2,
                        'description': 'Recipient language'
                    }
                },
                'order': 9,
                'group': 'basic-activity-information'
            },
            'activity-status': {
                'description': 'Activity status',
                'group': 'basic-activity-information',
                'order': 10
            },
            'activity-date': { 
                'description': 'Activity dates',
                'defining_attribute': 'type', 
                'defining_attribute_values': {
                    'start': {
                        'order': 1,
                        'description': 'Start Date'
                    },
                    'end': {
                        'order': 2,
                        'description': 'End Date'
                    }
                },
                'group': 'basic-activity-information',
                'order': 11
            },
            'contact-info': {
                'description': 'Contact information',
                'group': 'basic-activity-information',
                'order': 12
            },
            'participating-org': {
                'description': 'Participating organisation',
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'funding': {
                        'order': 1,
                        'description': 'Funding'
                    },
                    'extending': {
                        'order': 2,
                        'description': 'Extending'
                    },
                    'accountable': {
                        'order': 3,
                        'description': 'Accountable'
                    },
                    'implementing': {
                        'order': 4,
                        'description': 'Implementing'
                    }
                },
                'order': 13,
                'group': 'basic-activity-information'
            },
            'recipient-region': {
                'description': 'Recipient region',
                'group': 'geopolitical-information',
                'order': 14
            },
            'recipient-country': {
                'description': 'Recipient country',
                'group': 'geopolitical-information',
                'order': 15
            },
            'location': {
                'description': 'Sub-national geographic location',
                'group': 'geopolitical-information',
                'order': 16
            },
            'sector': {
                'description': 'Sector',
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'crs': {
                        'order': 1,
                        'description': 'DAC CRS'
                    },
                    'agency': {
                        'order': 2,
                        'description': 'Agency specific'
                    }
                },
                'group': 'classifications',
                'order': 17
            },
            'policy-marker': {
                'description': 'Policy marker',
                'group': 'classifications',
                'order': 18
            },
            'collaboration-type': {
                'description': 'Collaboration type',
                'group': 'classifications',
                'order': 19
            },
            'default-flow-type': {
                'description': 'Flow type',
                'group': 'classifications',
                'order': 20
            },
            'default-finance-type': {
                'description': 'Finance type',
                'group': 'classifications',
                'order': 21
            },
            'default-aid-type': {
                'description': 'Aid type',
                'group': 'classifications',
                'order': 22
            },
            'default-tied-status': {
                'description': 'Tied aid status',
                'group': 'classifications',
                'order': 23
            },
            'budget': {
                'description': 'Budget',
                'group': 'financial',
                'order': 24
            },
            'planned-disbursement': {
                'description': 'Planned disbursement',
                'group': 'financial',
                'order': 25
            },
            'budget-identifier': {
                'description': 'Budget identifier',
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'economic': {
                        'order': 1,
                        'description': 'Economic'
                    },
                    'administrative-functional': {
                        'order': 2,
                        'description': 'Administrative/functional'
                    }
                },
                'group': 'financial',
                'order': 26
            },
            'transaction': {
                'description': 'Transactions',
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'commitment': {
                        'order': 1,
                        'description': 'Commitment'
                    
                    },
                    'disbursement': {
                        'order': 2,
                        'description': 'Disbursement & Expenditure'
                    },
                    'reimbursement': {
                        'order': 3,
                        'description': 'Reimbursement'
                    },
                    'incoming': {
                        'order': 4,
                        'description': 'Incoming Funds'
                    },
                    'repayment': {
                        'order': 5,
                        'description': 'Loan repayment / interest repayment'
                    }
                },
                'group': 'financial-transaction',
                'order': 27
            },
            'document-link': {
                'description': 'Activity documents',
                'group': 'related-documents',
                'order': 28
            },
            'activity-website': {
                'description': 'Activity website',
                'group': 'related-documents',
                'order': 29
            },
            'related-activity': {
                'description': 'Related activity',
                'group': 'related-documents',
                'order': 30
            },
            'conditions': {
                'description': 'Conditions',
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'attached': {
                        'order': 1,
                        'description': 'Attached Y/N'
                    },
                    'text': {
                        'order': 2,
                        'description': 'Text'
                    }
                },
                'group': 'performance',
                'order': 31
            },
            'result': {
                'description': 'Results',
                'group': 'performance',
                'order': 32
            }
        })
    })
properties = {
    'under_consideration': { 
        'name': 'Under consideration',
        'group': 'publishing_timetable',
        'description': '',
        'data' : '',
        'type': 'code',
        'code': 'under_consideration'
        },
    'publishing_scope_value': { 
        'name': 'Scope',
        'group': 'publishing_scope',
        'description': '',
        'data' : 'schedule.find("publishing").find("scope").get("value")',
        'type': 'text'
        },
    'publishing_scope_narrative': 
        {
        'name': 'Scope narrative',
        'group': 'publishing_scope',
        'data' : 'schedule.find("publishing").find("scope").find("narrative").text',
        'type': 'text'
        },
    'publishing_timetable_date_initial': 
        {
        'name': 'Initial publication date',
        'group': 'publishing_timetable',
        'data' : 'schedule.find("publishing").find("publication-timetable").get("date-initial")',
        'type': 'text'
        },
    'publishing_timetable_narrative': 
        {
        'name': 'Timetable narrative',
        'group': 'publishing_timetable',
        'data' : 'schedule.find("publishing").find("publication-timetable").find("narrative").text',
        'type': 'text'
        },
    'publishing_frequency_frequency':
        {
        'name': 'Frequency',
        'group': 'publishing_frequency',
        'data' : 'schedule.find("publishing").find("publication-frequency").get("frequency")',
        'type': 'code',
        'code': 'frequency'
        },
    'publishing_frequency_timeliness':
        {
        'name': 'Timeliness',
        'group': 'publishing_frequency',
        'data' : 'schedule.find("publishing").find("publication-frequency").get("timeliness")',
        'type': 'code',
        'code': 'timeliness'
        },
    'publishing_frequency_narrative':
        { 
        'name': 'Frequency narrative',
        'group': 'publishing_frequency',
        'data' : 'schedule.find("publishing").find("publication-frequency").find("narrative").text',
        'type': 'text'
        },
    'publishing_lifecycle_point':
        { 
        'name': 'Lifecycle',
        'group': 'publishing_lifecycle',
        'data' : 'schedule.find("publishing").find("publication-lifecycle").get("point")',
        'type': 'code',
        'code': 'point'
        },
    'publishing_lifecycle_narrative':
        { 
        'name': 'Lifecycle narrative',
        'group': 'publishing_lifecycle',
        'data' : 'schedule.find("publishing").find("publication-lifecycle").find("narrative").text',
        'type': 'text'
        },
    'publishing_data_quality_quality':
        { 
        'name': 'Data quality',
        'group': 'publishing_data_quality',
        'data' : 'schedule.find("publishing").find("data-quality").get("quality")',
        'type': 'code',
        'code': 'quality'
        },
    'publishing_data_quality_narrative':
        { 
        'name': 'Data quality narrative',
        'group': 'publishing_data_quality',
        'data' : 'schedule.find("publishing").find("data-quality").find("narrative").text',
        'type': 'text'
        },
    'publishing_approach_resource':
        { 
        'name': 'Publishing approach',
        'group': 'publishing_approach',
        'data' : 'schedule.find("publishing").find("approach").get("resource")',
        'type': 'code',
        'code': 'resource'
        },
    'publishing_approach_narrative':
        { 
        'name': 'Publishing approach narrative',
        'group': 'publishing_approach',
        'data' : 'schedule.find("publishing").find("approach").find("narrative").text',
        'type': 'text'
        },
    'publishing_notes':
        { 
        'name': 'Notes',
        'group': 'publishing_notes',
        'data' : 'schedule.find("publishing").find("notes").find("narrative").text',
        'type': 'text'
        },
    'publishing_thresholds':
        { 
        'name': 'Threshold',
        'group': 'publishing_thresholds',
        'data' : 'schedule.find("publishing").find("thresholds").find("narrative").text',
        'type': 'text'
        },
    'publishing_exclusions':
        { 
        'name': 'Exclusions',
        'group': 'publishing_exclusions',
        'data' : 'schedule.find("publishing").find("exclusions").find("narrative").text',
        'type': 'text'
        },
    'publishing_constraints':
        {
        'name': 'Constraints',
        'group': 'publishing_constraints',
        'data' : 'schedule.find("publishing").find("constraints-other").find("narrative").text',
        'type': 'text'
        },
    'publishing_license':
        { 
        'name': 'Licence',
        'group': 'publishing_license',
        'data' : 'schedule.find("publishing").find("license").get("license")',
        'type': 'code',
        'code': 'license'
        },
    'publishing_license_narrative':
        { 
        'name': 'Licence narrative',
        'group': 'publishing_license',
        'data' : 'schedule.find("publishing").find("license").find("narrative").text',
        'type': 'text'
        },
    'publishing_multilevel':
        { 
        'name': 'Multilevel publication',
        'group': 'publishing_multilevel',
        'data' : 'schedule.find("publishing").find("activity-multilevel").get("yesno")',
        'type': 'code',
        'code': 'yesno'
        },
    'publishing_multilevel_narrative':
        { 
        'name': 'Multilevel publication narrative',
        'group': 'publishing_multilevel',
        'data' : 'schedule.find("publishing").find("activity-multilevel").find("narrative").text',
        'type': 'text'
        },
    'publishing_segmentation':
        { 
        'name': 'Segmentation',
        'group': 'publishing_segmentation',
        'data' : 'schedule.find("publishing").find("segmentation").get("segmentation")',
        'type': 'code',
        'code': 'segmentation'
        },
    'publishing_segmentation_narrative':
        { 
        'name': 'Segmentation narrative',
        'group': 'publishing_segmentation',
        'data' : 'schedule.find("publishing").find("segmentation").find("narrative").text',
        'type': 'text'
        },
    'publishing_user_interface_status':
        { 
        'name': 'User interface',
        'group': 'publishing_user_interface',
        'data' : 'schedule.find("publishing").find("user-interface").get("status")',
        'type': 'code',
        'code': 'status'
        },
    'publishing_user_interface_narrative':
        {
        'name': 'User interface narrative',
        'group': 'publishing_user_interface',
        'data' : 'schedule.find("publishing").find("segmentation").find("narrative").text',
        'type': 'text'
         },
    'schedule_type':
        {
        'name': 'Schedule type',
        'group': 'schedule_type',
        'data' : 'schedule.find("metadata").find("schedule_type").text',
        'type': 'text'
        },
    'schedule_type_code':
        {
        'name': 'Schedule type_code',
        'group': 'schedule_type',
        'data' : 'schedule.find("metadata").find("schedule_type").get("code")',
        'type': 'text'
        }
}
status = collections.OrderedDict({
              'fc': 'Fully compliant',
              'fp': 'Future publication',
              'pc': 'Partially compliant',
              'up': 'Not publishing now',
              'uc': 'Under consideration',
              'na': 'Not applicable'
         })


status_formatted = {
            'fc': {
                'name': 'Fully compliant',
                'class': 'icon-ok'
            },
            'fp': {
                'name': 'Future publication',
                'class': 'icon-wrench'
            },
            'pc': {
                'name': 'Partially compliant',
                'class': 'icon-flag'
            },
            'up': {
                'name': 'Not publishing now',
                'class': 'icon-remove'
            },
            'uc': {
                'name': 'Under consideration',
                'class': 'icon-refresh'
            },
            'na': {
                'name': 'Not applicable',
                'class': 'icon-remove'
            },
            '': {
                'name': '',
                'class': ''
            }
         }

codes = {   
    # Data quality
    'quality': {   'u': 'Unverified', 'v': 'Verified'},
    # Frequency
    'frequency': collections.OrderedDict({   'r': 'Real time',
                     'w': 'Weekly',
                     'f': 'Fortnightly',
                     'm': 'Monthly',
                     'o': 'Other',
                     'q': 'Quarterly',
                     'b': 'Bi-annually',
                     'a': 'Annually'}),
    # License type
    'license': collections.OrderedDict({    'p': 'Public domain',
                    'a': 'Attribution-only',
                    'o': 'Other (non-compliant)'
               }),
    # Lifecyle
    'point': {   'i': 'Implementation',
                 'o': 'Other',
                 'p': 'Pipeline/identification'},
    # Multi-level reporting
    'yesno': {   'n': 'No', 'y': 'Yes'},
    # Multi-level type
    'UNUSED': { 'b': 'Both',
                'h': 'Hierarchy',
                'r': 'Related activities'},
    # Segmentation
    'segmentation': {   'b': 'By country / region',
                        'o': 'Other',
                        's': 'Single file'},
    # Staff resource
    'UNUSED2': {  'a': 'Ad hoc',
                  'd': 'Dedicated resource',
                  'o': 'Other',
                  'w': 'Working group'},
    # System resource
    'resource': {  'd': 'Direct feed from internal systems',
                   'e': 'Excel spreadsheet conversion',
                   'm': 'Manual capture through an online tool (web entry platform)',
                   'o': 'Other'},
    # Timeliness
    'timeliness': collections.OrderedDict({  
                      'r': 'Real time',
                      '1w': '1 week in arrears',
                      '2w': '2 weeks in arrears',
                      '1m': '1 month in arrears',
                      '2m': '2 months in arrears',
                      '1q': '1 quarter in arrears',
                      'gt': '> 1 quarter in arrears',
                      'o': 'Other'}),
    # User interface
    'status': {   'i': 'In development',
                  'n': 'No',
                  'u': 'Under consideration',
                  'y': 'Yes'},

    # Under consideration
    'under_consideration': {   'on': 'Yes',
                       '': ''},
}
change_reasons = {
    'no_initial_date': 'No initial date provided',
    'no_date': 'No date provided',
    'initial_date': 'Initial date later',
    'parse_error': 'Not parsed properly',
    'typo': 'Fix typo',
    'missing': 'Information missing',
    'assumed': 'Information assumed',
    'inconsistent': 'Status/notes inconsistent'
}
