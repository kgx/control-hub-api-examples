#!/usr/bin/env python

# Module: migrate_jobs.py

"""
This script migrates active Jobs across sets of SDCs.

For example, if a set of SDCs has the label 'active' and another set of SDCs has the label
'standby', this script will swap those labels and then synchronize the Jobs.
Active Jobs with the label 'active' will follow the SDC labels and migrate to the new 'active' SDCs.

The script assumes no Jobs are running with the label 'standby'

Note that labels reported by SDCs themselves are immutable so this script only applies
to SDC labels set within Control Hub

Usage: python migrate_jobs.py <sch_url> <active_label> <standby_label> <sch_session_token> [DRY_RUN | DO_IT]

Example: python migrate_jobs.py https://cloud.streamsets.com active standby $SESSION_TOKEN DRY_RUN
"""

# Imports
import os
import sys

# The path below assumes the script used to launch this process
# is located at '../bin/' relative to the location of this file
sys.path.append(os.getcwd() + '/../python/utils')
from utils import ControlHubApiHelper, ControlHubApiException
from utils import SDCHelper, SDCValidationException
from utils import JobHelper, JobValidationException
from utils import print_helper
from utils import properties as props

def get_args():
    global sch_url
    global active_label
    global standby_label
    global session_token
    global dry_run

    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print(props.USAGE_MESSAGE)
        quit(-1)

    sch_url = sys.argv[1]
    active_label = sys.argv[2]
    standby_label = sys.argv[3]
    session_token = sys.argv[4]

    # A 'Dry Run' prints output to screen without taking any action
    if len(sys.argv) == 6 and sys.argv[5] == 'DO_IT':
        dry_run = False
    else:
        dry_run = True

def init():
    """
    Initializes the ControlHubApiHelper, SDCHelper and JobHelper
    and prints startup messages
    """
    global control_hub_api
    global sdc_helper
    global job_helper

    get_args()

    if dry_run:
        print_helper.print_banner('Dry Run (No changes will be made)', 2, 0)
    else:
        print('')
    print_helper.print_message('Connecting to Control Hub at {}'.format(sch_url), 1)

    # Init our helper objects
    control_hub_api = ControlHubApiHelper(sch_url, session_token)
    sdc_helper = SDCHelper(control_hub_api, active_label, standby_label)
    job_helper = JobHelper(control_hub_api, sdc_helper, active_label, standby_label)
    
    print_helper.print_message('Using the labels \'{}\' and \'{}\''.format(active_label, standby_label), 1, 0)

def main():

    try:

        # Connect to Control Hub and initialize the helper objects
        init()

        # Get the SDCs
        sdc_helper.get_sdcs()

        # Make sure the SDCs are in a good state for Job migration
        sdc_helper.validate_sdcs()

        # Print the SDCs
        sdc_helper.print_sdcs()

        # Get the Jobs to be migrated
        job_helper.get_jobs()

        # Make sure the Jobs are in a good state to be migrated
        job_helper.validate_jobs()

        # Print the jobs
        job_helper.print_jobs_before()

        # Stop here if a dry run
        if dry_run:
            print_helper.print_banner('End of Dry Run')
        else:

            # Swap the labels on the SDCs
            sdc_helper.update_sdc_labels()

            # Synchronize the Jobs
            job_helper.sync_jobs()

            # Print the Jobs after synchronization to confirm they are running on the new SDCs
            job_helper.print_jobs_after()

        print_helper.print_message('Done', 2, 2)

    except (ControlHubApiException, SDCValidationException, JobValidationException) as e:
        print_helper.print_exception(e)
        raise e

main()