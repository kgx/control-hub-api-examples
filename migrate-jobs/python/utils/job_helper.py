#!/usr/bin/env python

# Module: job_helper
"""Implements the class JobHelper"""

import print_helper
import properties as props
from job_validator import JobValidator, JobValidationException

# The list of Jobs to migrate
jobs = []

class JobHelper:

    def __init__(self, control_hub_api_param, sdc_helper_param, active_label_param, standby_label_param):
        global control_hub_api
        global sdc_helper
        global active_label
        global standby_label

        control_hub_api = control_hub_api_param
        sdc_helper = sdc_helper_param
        active_label = active_label_param
        standby_label = standby_label_param

    def get_jobs(self):
        """
        Get Active Jobs that reference active_label (i.e. the Jobs to migrate)

        :raises JobValidationException: if no active Jobs are found with active_label
        """

        global jobs

        jobs.clear()

        # Get the list of Active Jobs from Control Hub
        active_jobs = control_hub_api.get_active_jobs()

        # Exit if no Active Jobs found
        if not active_jobs:
            raise JobValidationException(props.JOBS_INVALID_NO_ACTIVE_JOBS)

        # Find Active Jobs with active_label
        for job in active_jobs:
            if active_label in job['labels']:
                jobs.append(job)

        # Exit if no Active Jobs with active_label are found
        if not jobs:
            raise JobValidationException(props.JOBS_INVALID_NO_ACTIVE_JOBS_WITH_LABEL.format(active_label))

    def validate_jobs(self):
        """
        Makes sure Jobs are in a good state for migration
        @:raises: JobValidationException
        """
        job_validator = JobValidator(sdc_helper, active_label)
        job_validator.validate_jobs(jobs)

    def print_jobs_before(self):
        print_helper.print_message(props.JOBS_TO_BE_MIGRATED_MESSAGE.format(active_label), 2, 0)
        print_helper.print_pipelines_for_jobs(active_label, jobs, sdc_helper.sdcs)

    def print_jobs_after(self):
        print_helper.print_message(props.JOBS_AFTER_MIGRATION_MESSAGE.format(active_label), 2, 0)
        print_helper.print_pipelines_for_jobs(active_label, jobs, sdc_helper.sdcs)


    def sync_jobs(self):
        """ Calls the Control Hub API to Synchronize the set of Jobs to be migrated """
        print_helper.print_banner(props.SYNCING_JOBS_MESSAGE)

        # Get the list of Job IDs for the Jobs to be migrated
        job_ids = []
        for job in jobs:
            job_ids.append(job['id'])
            print_helper.print_message(props.SYNCING_JOB_MESSAGE.format(job['name']))

        # Call the Control Hub API to Sync the jobs
        control_hub_api.sync_jobs(job_ids)

        # Refresh the cached Job info
        self.get_jobs()

        print_helper.print_banner(props.SYNCING_JOBS_COMPLETE_MESSAGE, 0, 0)

class JobValidationException(Exception):
    pass