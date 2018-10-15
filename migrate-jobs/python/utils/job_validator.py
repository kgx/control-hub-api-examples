#!/usr/bin/env python

# Module: job_validator
"""
Validates Jobs are in a good state for Job Migration.
Raises a  JobValidationException if this is not the case.

Validation rules include:

    - Insure Jobs are in sync before migration

"""
# Imports
from sdc_helper import SDCHelper
import properties as props

class JobValidator:

    def __init__(self, sdc_helper_param, active_label_param):
        global sdc_helper
        global active_label
        sdc_helper = sdc_helper_param
        active_label = active_label_param

    def validate_jobs(self, jobs):
        """
        Make sure the Jobs to be migrated are synchronized before we change anything

        :raises JobValidationException: if Jobs are not synchronized
        """
        self.validate_jobs_are_in_sync(jobs)

    def validate_jobs_are_in_sync(self, jobs):
        # For each active job with active_label...
        for job in jobs:

            # For each SDC the Job is running on (might be more than 1)...
            for sdc_id in job['currentJobStatus']['sdcIds']:

                # If the SDC does not have active_label...
                if sdc_id not in sdc_helper.get_active_sdc_ids():

                    # Bail out
                    raise JobValidationException(
                        props.JOBS_INVALID_OUT_OF_SYNC.format(job['name'], active_label, sdc_id, active_label))



class JobValidationException(Exception):
    pass
