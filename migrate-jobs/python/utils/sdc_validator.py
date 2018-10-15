#!/usr/bin/env python

# Module: sdc_validator
"""Implements the classes SDCValidator and SDCValidationException"""

# Imports
import properties as props

class SDCValidator:
    """
    Validates SDCs are in a good state for Job Migration.
    Raises an SDCValidationException if this is not the case.

    Validation rules include:

        - There is at least one SDC for both labels
        - No Edge Data Collectors are included in the list
        - No SDC has one of the labels as a "fixed" (immutable) label
        - No SDC has both labels
    """

    def __init__(self, active_label_param, standby_label_param):
        global active_label
        global standby_label

        active_label = active_label_param
        standby_label = standby_label_param

    def validate_sdcs(self, sdcs, active_sdcs, standby_sdcs):
        """Runs the SDC validation rules """

        # Validations for all SDCs
        self.validate_all_sdcs(sdcs)

        # Validate Active SDCs
        self.validate_sdcs_with_label(active_sdcs, active_label)

        # Validate Standby SDCs
        self.validate_sdcs_with_label(standby_sdcs, standby_label)


    def validate_all_sdcs(self,sdcs):
        """Validation rules to be run across all SDCs"""
        for sdc in sdcs.values():
            self.validate_not_fixed_label(sdc)

    def validate_sdcs_with_label(self, sdcs, label):
        """Runs validation rules for a list of SDCs with a given label"""
        self.validate_at_least_one_sdc_with_label(sdcs, label)
        for sdc in sdcs:
            self.validate_not_edge_sdc(sdc)
            self.validate_not_both_labels(sdc)

    def validate_at_least_one_sdc_with_label(self, sdcs, label):
        """
        Check if there is at least one SDC with the label
        :raises: SDCValidationException
        """
        if not sdcs:
            raise SDCValidationException(props.SDCS_INVALID_INSUFFICIENT_SDCS.format(label))

    def validate_not_edge_sdc(self, sdc):
        """
        Makes sure there are no Edge Data Collectors
        :raises: SDCValidationException
        """
        if sdc['edge']:
            raise SDCValidationException(props.SDCS_INVALID_EDGE.format(sdc['httpUrl']))

    def validate_not_fixed_label(self, sdc):
        """
        Make sure the label to be changed is not a fixed label
        :raises: SDCValidationException
        """
        if active_label in sdc['reportedLabels']:
            raise SDCValidationException(props.SDCS_INVALID_FIXED_LABEL.format(sdc['httpUrl'], active_label))
        if standby_label in sdc['reportedLabels']:
            raise SDCValidationException(props.SDCS_INVALID_FIXED_LABEL.format(sdc['httpUrl'], standby_label))

    def validate_not_both_labels(self, sdc):
        """
        Make sure the SDC does not have both labels
        :raises: SDCValidationException
        """
        if active_label in sdc['labels'] and standby_label in sdc['labels']:
            raise SDCValidationException(
                props.SDCS_INVALID_HAS_BOTH_LABELS.format(sdc['httpUrl'], active_label, standby_label))

class SDCValidationException(Exception):
    pass
