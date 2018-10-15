#!/usr/bin/env python

###############################################################
##
## start_job_with_custom_params.py
##
## Starts a Control Hub Job with custom parameter values
##
## Usage: python start_job_with_custom_params.py <SCH_URL> <JOB_ID> <PARAMS> <SESSION_TOKEN>
##
## Example: python start_job_with_custom_params.py https://acme.org db26385e-2cf2-4e63-a52b-61369396cdc9:globex  '{"OUTPUT_DIR":"/tmp/out/dir45","FILE_PREFIX":"mark_45_"}' $SESSION_TOKEN
##
###############################################################

## Imports
import requests
import sys

## Command line args
if len(sys.argv) != 5 :
  print ('Error: Wrong number of arguments')
  print ('Usage: python start_job_with_custom_params.py <SCH_URL> <JOB_ID> <PARAMS> <SESSION_TOKEN>')
  quit(1)

sch_url = sys.argv[1];
job_id = sys.argv[2]
params = sys.argv[3]
session_token = sys.argv[4]


## Common headers for API calls
api_headers = {}
api_headers['Content-type'] = 'application/json'
api_headers['X-Requested-By'] = 'SDC'
api_headers['X-SS-REST-CALL'] = 'true'
api_headers['X-SS-User-Auth-Token'] = session_token

print('Connecting to Control Hub at {}'.format(sch_url))

## Get the Existing Job
print('Retrieving  Job ID {}'.format(job_id))
endpoint_url = '{}/jobrunner/rest/v1/job/{}'.format(sch_url,job_id)
response = requests.get( url = endpoint_url, headers = api_headers)
if response.status_code != 200: 
    print('Error getting Job')
    print(response.status_code)
    print(response)
    exit (-1)
job = response.json()
print('The Job\'s existing Parameters are: \'{}\''.format(job['runtimeParameters']))

## Set the new Parameters
print('Setting the Job\'s Parameters to the new value: \'{}\''.format(params))
job['runtimeParameters'] = params

## Update the Job within Control Hub
print('Saving the modified Job on Control Hub') 
response = requests.post( url = endpoint_url, headers = api_headers, json=job)
if response.status_code != 200: 
    print('Error updating Job')
    print(response.status_code)
    print(response)
    exit (-1)

## Start the updated Job
print('Starting the updated Job')
endpoint_url = '{}/jobrunner/rest/v1/job/{}/start'.format(sch_url,job_id) 
response = requests.post( url = endpoint_url, headers = api_headers)
if response.status_code != 200: 
    print('Error starting Job')
    print(response.status_code)
    print(response)
    exit (-1)

print('Done')


