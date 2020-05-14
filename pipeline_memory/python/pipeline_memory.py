#!/usr/bin/env python

###############################################################
##
## create_job_for_pipeline.py
##
## Creates a StreamSets Control Hub Job using the latest commit 
## and parameter values for a given Pipeline 
##
###############################################################

## Imports
import json
import requests
import sys
import re



  
sch_url = "https://cloud.streamsets.com"
session_token = sys.argv[2]

## Defaults for Job properties
default_stats_refresh_interval = 60000
default_num_instances = 1
default_migrate_offsets = False
default_edge = False

print("\nConnecting to Control Hub at " + sch_url)

#################################
## Common headers for API calls
#################################
api_headers = {}
api_headers['Content-type'] = 'application/json'
api_headers['X-Requested-By'] = 'SDC'
api_headers['X-SS-REST-CALL'] = 'true'
api_headers['X-SS-User-Auth-Token'] = session_token

#################################
## Get latest commit for Pipeline
#################################

## Create the endpoint URL
endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelines/'
response = requests.get( url = endpoint_url, headers = api_headers)
# print(response.text)
pipelines = json.loads(response.text)["data"]
spark_driver_memory = 0
spark_executor_memory = 0

for pipeline in pipelines:
    pipeline_id = pipeline["pipelineId"]
    commit_id = pipeline["commitId"]


    runtime_parameters = {}
    spark_config = {}
    ## Create the endpoint URL
    endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelineCommit/' + commit_id

    ## Call the API 
    response = requests.get( url = endpoint_url, headers = api_headers )

    if response.status_code != 200: 
        print('Error getting runtime parameters for latest commit')
        print(response.status_code)
        print(response.text)
        exit (-1)

    pipeline_definition = json.loads(response.json()['pipelineDefinition'])
    #print("pipelineDefinition: {}", pipeline_definition)

    configuration = pipeline_definition['configuration']

    for item in configuration:
        if item['name'] == 'constants':
            for param in item['value']:
                runtime_parameters[param['key']] = param['value']
        if item['name'] == 'sparkConfigs':
            for param in item['value']:
                key = param['key']
                value = param['value']
                spark_config[key] = value
                if key == "spark.driver.memory":
                    spark_driver_memory += int(value.replace("G", ""))
                    print(str.format("Executor: {}, Driver: {}", spark_executor_memory, spark_driver_memory))
                if key == "spark.executor.memory":
                    spark_executor_memory += int(value.replace("G", ""))
                    print(str.format("Executor: {}, Driver: {}", spark_executor_memory, spark_driver_memory))




print(str.format("Executor: {}, Driver: {}", spark_executor_memory, spark_driver_memory))

## Create the endpoint URL
# endpoint_url = sch_url + '/jobrunner/rest/v1/jobs/createJobs'

## Set the Job's configuration
# job_config = {}
# job_config['name'] = 'Job for ' + latest_commit['name']
# job_config['description'] = latest_commit['description']
# job_config['pipelineName'] = latest_commit['name']
# job_config['pipelineId'] = pipeline_id
# job_config['pipelineCommitId'] = latest_commit['commitId']
# job_config['rulesId'] = latest_commit['currentRules']['id']
# job_config['pipelineCommitLabel'] = 'v' + latest_commit['version']
# job_config['labels'] = labels
# job_config['statsRefreshInterval'] = default_stats_refresh_interval
# job_config['numInstances'] = default_num_instances
# job_config['migrateOffsets'] = default_migrate_offsets
# job_config['edge'] = default_edge
# job_config['runtimeParameters'] = json.dumps(runtime_parameters)


# print('\n** Job Configuration *******************')
# for key in job_config.keys():
#     if key == 'labels':
#         print ('labels : ' + json.dumps(job_config['labels']))
#     elif key == 'runtimeParameters':
#         print ('runtimeParameters : ' + json.dumps(job_config['runtimeParameters']))
#     else:
#         print(key + ' : ' + str(job_config[key]))

# ## Set the job_data as the payload
# payload = [job_config]

## Call the API 
#response = requests.put( url = endpoint_url, headers = api_headers, json = payload )

# if response.status_code != 200: 
#     print('Error creating job')
#     print(response.status_code)
#     print(response.text)
#     exit (-1)

# job = response.json()[0]

# print('\nJob created successfully!')

# print('Job ID: ' + job['id'])
# print('\nDone')