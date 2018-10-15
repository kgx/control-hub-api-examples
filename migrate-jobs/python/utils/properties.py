#!/usr/bin/env python

# Module: properties

USAGE_MESSAGE = '\n\nError: Wrong number of arguments\n' \
    + 'Usage: python migrate_jobs.py <sch_url> <label_1> <label_2> <sch_session_token> [DRY_RUN | DO_IT]\n' \
    + 'Example: python migrate_jobs.py https://cloud.streamsets.com prod standby $SESSION_TOKEN DRY_RUN'

# Control Hub API Endpoints
API_ENDPOINT_GET_ACTIVE_JOBS = '/jobrunner/rest/v1/jobs/byStatus?jobStatus=ACTIVE&orderBy=NAME&order=ASC'
API_ENDPOINT_GET_CURRENT_USER = '/security/rest/v1/currentUser'
API_ENDPOINT_GET_SDCS = '/jobrunner/rest/v1/sdcs'
API_ENDPOINT_SYNC_JOBS = '/jobrunner/rest/v1/jobs/syncJobs'
API_ENDPOINT_UPDATE_LABELS = '/jobrunner/rest/v1/sdc/{}/updateLabels'

# Control Hub API error messages
API_GET_ERROR = 'Error in GET operation calling the endpoint \'{}\''
API_POST_ERROR = 'Error in POST operation calling the endpoint \'{}\' with payload \'{}\''

# SDC info messsages
SDC_LIST_MESSAGE = 'Current Data Collectors and labels before making any changes:'
SDC_SWAP_LABLES_MESSAGE = 'Replacing Data Collector Label \'{}\' with \'{}\' for SDC at {}'

# Job info messages
JOBS_TO_BE_MIGRATED_MESSAGE = 'Jobs to be migrated (Active Jobs with the label \'{}\'):'
JOBS_AFTER_MIGRATION_MESSAGE = 'Active Jobs with the label \'{}\' after migration:'

# Synchronizing Job messages
SYNCING_JOBS_MESSAGE = 'Synchronizing Jobs:'
SYNCING_JOB_MESSAGE = 'Synchronizing Job: {}'
SYNCING_JOBS_COMPLETE_MESSAGE = 'Synchronizing Jobs Complete'

# SDC Validation error messages
SDCS_INVALID_EDGE = \
    'The SDC at {} is an Edge Data Collector.\nMigration of Jobs is not supported for Edge Data Collectors'
SDCS_INVALID_FIXED_LABEL = \
    'The SDC at {} has \'{}\' \nas a Reported Label which cannot be changed'
SDCS_INVALID_HAS_BOTH_LABELS = \
    'The SDC at {} has both labels \n\'{}\' and \'{}\' so swapping labels will have no effect'
SDCS_INVALID_INSUFFICIENT_SDCS = \
    'No SDCs with the label \'{}\' are running.'

# Job Validation error messages
JOBS_INVALID_NO_ACTIVE_JOBS = 'No Jobs are currently Active'
JOBS_INVALID_NO_ACTIVE_JOBS_WITH_LABEL = 'No Active Jobs with label \'{}\' are running.'
JOBS_INVALID_OUT_OF_SYNC = \
    'The Job \'{}\' with label \'{}\' ' \
    '\nis running on an SDC with the id \'{}\''\
    '\nthat does not have the label \'{}\'.' \
    '\nMake sure Jobs are Synchronized before running this script.'

