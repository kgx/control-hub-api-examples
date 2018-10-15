#!/usr/bin/env python

# Module: sdc_helper
"""Implements the class SDCHelper"""

# Imports
from sdc_validator import SDCValidator
import print_helper
import properties as props

class SDCHelper:

    # Dictionary of SDCs keyed by sdcId
    @property
    def sdcs(self):
        return sdcs

    def __init__(self, control_hub_api_param, active_label_param, standby_label_param):
        global control_hub_api
        global active_label
        global standby_label

        control_hub_api = control_hub_api_param
        active_label = active_label_param
        standby_label = standby_label_param

    def get_sdcs(self):
        """
        Gets SDCs from Control Hub and populates the instance
        variables active_sdcs and standby_sdcs

        :raises: SDCValidationException if we don't find at least one of each
        """
        global sdcs
        global active_sdcs
        global standby_sdcs

        sdcs = {}
        active_sdcs = []
        standby_sdcs = []

        for sdc in self.get_sdcs_from_control_hub():

            # Store all SDCs in the dictionary keyed by sdcId
            sdcs[sdc['id']] = sdc

            # Store SDCs with active_label
            if active_label in sdc['labels']:
                active_sdcs.append(sdc)

            # Store SDCs with standby_label
            elif standby_label in sdc['labels']:
                standby_sdcs.append(sdc)

    def get_sdcs_from_control_hub(self):
        """Returns a sorted list of SDCs retrieved from Control Hub"""
        # Get the list of SDCs from Control Hub
        sdcs = control_hub_api.get_sdcs()

        # Flatten the label arrays in the SDC records
        for sdc in sdcs:
            sdc['reported_labels_string'] = ','.join(sdc['reportedLabels'])
            sdc['labels_string'] = ','.join(sdc['labels'])

        return sdcs

    def update_sdc_labels(self):
        """ Swaps active_label and standby_label on the matching SDCs """
        print_helper.print_banner('Swapping Data Collector Labels:')
        self.update_labels_for_sdcs(active_sdcs, active_label, standby_label)
        self.update_labels_for_sdcs(standby_sdcs, standby_label, active_label)

        # refresh our cached SDC info
        self.get_sdcs()

    def update_labels_for_sdcs(self, sdcs, label_to_remove, label_to_add):
        """ Swaps an old for a new label for a list of SDCs """
        for sdc in sdcs:
            print(props.SDC_SWAP_LABLES_MESSAGE.format(label_to_remove, label_to_add, sdc['httpUrl']))

            # Remove the old label from the SDC
            sdc['labels'].remove(label_to_remove)

            # Add the new label to the SDC
            sdc['labels'].append(label_to_add)

            # Call the Control Hub API to set the updated SDC labels
            control_hub_api.update_sdc_labels(sdc['id'], sdc['labels'])

    def get_active_sdc_ids(self):
        active_sdc_ids = []
        for sdc in active_sdcs:
            active_sdc_ids.append(sdc['id'])
        return active_sdc_ids

    def validate_sdcs(self):
        sdc_validator = SDCValidator(active_label, standby_label)
        sdc_validator.validate_sdcs(sdcs, active_sdcs, standby_sdcs)

    def print_sdcs(self):
        print_helper.print_message(props.SDC_LIST_MESSAGE, 1)
        print_helper.print_sdcs_with_label(active_label, active_sdcs)
        print_helper.print_sdcs_with_label(standby_label, standby_sdcs)

class SDCValidationException(Exception):
    pass
