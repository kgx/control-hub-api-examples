#!/usr/bin/env python

# Module: print_helper
"""Some handy routines for printing info to the console"""

HORIZONTAL_RULE_CHAR = '-'
HORIZONTAL_RULE_LENGTH = 88
HORIZONTAL_RULE = HORIZONTAL_RULE_CHAR * HORIZONTAL_RULE_LENGTH
FORMAT_STRING = '{:<40s}{:<30s}{:<50s}'

def print_message(message, num_leading_newlines=None, num_trailing_newlines=None):
    """Prints a message with optional leading and trailing newlines"""
    line = ''
    if num_leading_newlines is not None:
        line = '\n' * num_leading_newlines
    line += message
    if num_trailing_newlines is not None:
        line += '\n' * num_trailing_newlines
    print(line)

def print_horizontal_rule(num_leading_newlines=None, num_trailing_newlines=None):
    """Prints a horizontal_rule with optional leading and trailing newlines"""
    print_message(HORIZONTAL_RULE, num_leading_newlines, num_trailing_newlines)

def print_banner(message, num_leading_newlines=None, num_trailing_newlines=None):
    """Prints a message between two horizontal_rule with optional leading and trailing newlines"""
    print_horizontal_rule(num_leading_newlines)
    print_message(message)
    print_horizontal_rule(0, num_trailing_newlines)

def print_sdc_list_header(label_name):
    """prints a headline with label for a list of SDCs"""
    message = FORMAT_STRING.format(
        'SDCs with the label \'{}\''.format(label_name),
        'Fixed Labels',
        'Control Hub Labels')
    print_banner(message, 1)

def print_sdc(sdc):
    """Prints an SDC with its URL and labels"""
    print(FORMAT_STRING.format(sdc['httpUrl'], sdc['reported_labels_string'], sdc['labels_string']))

def print_sdcs_with_label(label, sdcs):
    """Prints a set of SDC with a label"""
    print_sdc_list_header(label)
    if not sdcs:
        print('No SDCs found for this label')
    else:
        for sdc in sdcs:
            print_sdc(sdc)

def print_pipeline_instance(job_name, pipeline_name, sdc_url):
    """Prints a pipeline instance with Job name and SDC URL"""
    print(FORMAT_STRING.format(job_name, pipeline_name, sdc_url))

def print_job_list_header(label):
    """prints a header line with label for a list of Jobs"""
    message = FORMAT_STRING.format('Job Name', 'Pipeline Name','SDC URL(s)')
    print_banner(message, 0, 0)

def print_pipelines_for_jobs(label, jobs, sdcs):
    """
    Prints a list of Pipeline instances and SDC URLs for a set of Jobs identified by a label
    """
    print_job_list_header(label)

    for job in jobs:
        first_instance_of_pipeline_for_job = True

        # For each SDC running a pipeline instance for the Job...
        for sdc_id in job['currentJobStatus']['sdcIds']:

            # If it's the first instance, print the Job Name
            if first_instance_of_pipeline_for_job:
                print_pipeline_instance(job['name'], job['pipelineName'], sdcs[sdc_id]['httpUrl'])

            # If it's not the first instance only print the SDC URL
            else:
                print_pipeline_instance('', '', sdcs[sdc_id]['httpUrl'])

            first_instance_of_pipeline_for_job = False
        print('')

def print_exception(e):
    print_horizontal_rule(1)
    print_message('An Exception has occurred: ', 0, 0)
    print_message('{}: {}'.format(type(e).__name__, e), 0, 0)
    print_horizontal_rule(0, 1)