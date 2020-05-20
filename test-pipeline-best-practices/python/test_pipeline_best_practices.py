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


## Command line args
if len(sys.argv) != 4:
  print ("Error: Wrong number of arguments")
  print ("Usage: python create_job_for_pipeline.py <sch_url> <pipeline_id> <sch_session_token> ")
  quit(1)
  
sch_url = sys.argv[1];
pipeline_id = sys.argv[2]
session_token = sys.argv[3]

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
print('\nGetting latest commit for pipeline ID: ' + pipeline_id + '\n')

## Create the endpoint URL
endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelines/latestCommit'

## Set the pipeline_id as the payload
payload = [pipeline_id]

## Call the API 
response = requests.post( url = endpoint_url, headers = api_headers, json = payload )

if response.status_code != 200: 
    print('Error getting latest commit')
    print(response.status_code)
    print(response.text)
    exit (-1)

latest_commit = response.json()[0]

## Extract the label text from each Label object 
labels = []
for label in latest_commit['pipelineLabels']:
    labels.append(label['label'])

print('** Latest Commit *************************')
print('Pipeline ID : ' + pipeline_id)
print('Pipeline Name : ' + latest_commit['name'])
print('Description : ' + latest_commit['description'])
print('Version : ' + latest_commit['version'])
print('Commit ID : ' + latest_commit['commitId'])
print('Rules ID : ' + latest_commit['currentRules']['id'])
print('Pipeline Labels : ' + json.dumps(labels))

###########################################
## Get runtime parameters for latest commit
###########################################
print('\nGetting runtime parameters for commit ID: ' + latest_commit['commitId'] + '\n')

runtime_parameters = {}

## Create the endpoint URL
endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelineCommit/' + latest_commit['commitId']

## Call the API 
response = requests.get( url = endpoint_url, headers = api_headers )

if response.status_code != 200: 
    print('Error getting runtime parameters for latest commit')
    print(response.status_code)
    print(response.text)
    exit (-1)

pipeline_definition = json.loads(response.json()['pipelineDefinition'])
print("pipelineDefinition: {}", pipeline_definition)

configuration = pipeline_definition['configuration']
for item in configuration:
    if item['name'] == 'constants':
        for param in item['value']:
            runtime_parameters[param['key']] = param['value']
        break

if len(runtime_parameters) == 0:
    print('No Runtime Parameters found for commit')
else:
    print('** Runtime Parameters ********************')
    for key in runtime_parameters:
        print(key + ' : ' + runtime_parameters[key])
 if item['name'] == 'sparkConfigs':
    pipeline_count += 1
    for param in item['value']:
        key = param['key']
        value = param['value']
        spark_config[key] = value
        if key == "spark.driver.cores":
            spark_driver_cores += int(value)
        if key == "spark.executor.cores":
            spark_exectutor_cores += int(value)
            print(str.format("{} - Executor: {}g {} cores, Driver: {}g {} cores", pipeline_count, spark_executor_memory, spark_exectutor_cores, spark_driver_memory, spark_driver_cores))
        if key == "spark.driver.memory":
            spark_driver_memory += int(value.replace("G", ""))
        if key == "spark.executor.memory":
            spark_executor_memory += int(value.replace("G", ""))

            
###############
## Create a Job
###############
print('Testing Job')

stages = pipeline_definition['stages']
for stage in stages: 
    label = stage["uiInfo"]["label"]
    clean_label = re.sub(r"[\s\d_-]","",label)
    instance_name = re.sub("_.*","",stage["instanceName"])
    #print("checking stage " + instance_name + "(" + clean_label + ")")
    if re.match(r".*\d$", label) or clean_label == instance_name:
        print("Detected non-descriptive label: " + label)

    if stage["library"] == "streamsets-spark-snowflake-lib":
        stage_config = stage['configuration']
        for item in stage_config:
            if item['name'] == 'conf.readMode' and item["value"] != "QUERY":
                print("Detected non-query mode Snowflake Origin: " + label)
            if item['name'] == 'conf.query' and re.match(r".*FROM [^\$\.] (where.*)?$", item["value"]):
                print("Detected invalid query " + label)

   






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