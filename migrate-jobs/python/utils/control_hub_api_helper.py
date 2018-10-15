#!/usr/bin/env python

# Module: control_hub_api_helper
"""
Implements the classes ControlHubApiHelper and ControlHubApiException
which provide convenience methods to call a set of Control Hub REST 
API endpoints.
"""
# Imports
import requests
import properties as props
import print_helper

class ControlHubApiHelper:
    """
    Example Usage of this class by a client:

    # Create an instance passing in a Control Hub URL and session token
    control_hub_api = ControlHubApiHelper(sch_url, session_token)

    # Call a method
    try:
      sdcs = control_hub_api.get_sdcs()

    # Catch an Exception
    except ControlHubApiException as e:
      ...
    """

    def __init__(self, sch_url_param, session_token_param):
        """
        Initializes a session to interact with Control Hub.

        :param sch_url_param: the Control Hub base URL
        :param session_token_param: a Control Hub Session Token
        :raises: ControlHubApiException if a test API call fails
        """
        global sch_url
        sch_url = sch_url_param

        self.init_session(session_token_param)

        # Try a simple API call to validate the Control Hub connection
        # No need to return a result if successful; we'll raise an Exception
        # if there is a problem
        self.control_hub_get(props.API_ENDPOINT_GET_CURRENT_USER)

    def init_session(self, session_token_param):
        """Inits the session with the Control Hub API headers"""

        global session

        headers = {'Content-Type':'application/json'}
        headers['X-Requested-By'] = 'SDC'
        headers['X-SS-REST-CALL'] = 'true'
        headers['X-SS-User-Auth-Token'] = session_token_param

        session = requests.session()
        session.headers = headers

    def control_hub_get(self, endpoint):
        """
        Handles a Control Hub GET operation

        :param endpoint: the Control Hub endpoint to be appended to the base URL
        :return: JSON formatted Control Hub API response
        :raises: ControlHubApiException
        """
        response = session.get(sch_url + endpoint)
        if response.status_code != 200:
            print_helper.print_message(props.API_GET_ERROR.format(endpoint), 1)
            raise ControlHubApiException(response)
        return response.json()

    def control_hub_post(self, endpoint, payload):
        """
        Handles a Control Hub POST operation

        :param endpoint: the Control Hub endpoint to be appended to the base URL
        :return: Control Hub API response (callers may choose to ignore the response)
        :raises: ControlHubApiException
        """
        response = session.post(url=sch_url + endpoint, json=payload)
        if response.status_code != 200:
            print_helper.print_message(props.API_POST_ERROR.format(endpoint, payload))
            raise ControlHubApiException(response)
        return response


    # Control Hub API methods
    def get_sdcs(self):
        return self.control_hub_get(props.API_ENDPOINT_GET_SDCS)

    def get_active_jobs(self):
        return self.control_hub_get(props.API_ENDPOINT_GET_ACTIVE_JOBS)

    def update_sdc_labels(self, sdc_id, labels):
        endpoint = props.API_ENDPOINT_UPDATE_LABELS.format(sdc_id)
        payload = {'id':sdc_id, 'labels':labels}
        return self.control_hub_post(endpoint, payload)

    def sync_jobs(self, job_ids):
        return self.control_hub_post(props.API_ENDPOINT_SYNC_JOBS, job_ids)


class ControlHubApiException(Exception):
    pass
