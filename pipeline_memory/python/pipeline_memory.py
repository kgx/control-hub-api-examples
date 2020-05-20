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
endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelines?onlyPublished=true&executionModes=STREAMING&pipelineLabelId=Stage_To_Rawvault:k12.com&orderBy=LAST_MODIFIED_ON&order=DESC'
response = requests.get( url = endpoint_url, headers = api_headers)
# print(response.text)
pipelines = json.loads(response.text)["data"]
spark_driver_memory = 0
spark_executor_memory = 0
spark_exectutor_cores = 0
spark_driver_cores = 0
pipeline_count = 0
for pipeline in pipelines:
    pipeline_id = pipeline["pipelineId"]
    commit_id = pipeline["commitId"]

    ## Create the endpoint URL
    ## Call the API 
    # response = requests.get( url = endpoint_url, headers = api_headers )
    
    #create a draft of the pipeline off of the latest commit
    response = requests.post(str.format("https://cloud.streamsets.com/pipelinestore/rest/v1/pipelineCommit/{}/createDraft",commit_id), headers=api_headers)

    if response.status_code != 200: 
        print('Error getting runtime parameters for latest commit')
        print(response.status_code)
        print(response.text)
        exit (-1)
    # print(response.text)
    
    commit = response.json()

    runtime_parameters = {}
    spark_config = {}
    pipeline_definition = json.loads(commit['pipelineDefinition'])
    #print("pipelineDefinition: {}", pipeline_definition)
    print(json.dumps(pipeline_definition))
    configuration = pipeline_definition['configuration']
    title = pipeline_definition["title"]
    min_executors = 0
    max_executors = 0
    dynamic_allocation = False
    for item in configuration:
        if item['name'] == 'constants':
            for param in item['value']:
                runtime_parameters[param['key']] = param['value']
        if item['name'] == 'sparkConfigs':
            pipeline_count += 1
            for param in item['value']:
                key = param['key']
                value = param['value']
                spark_config[key] = value
                if key == "spark.driver.cores":
                    spark_driver_cores = int(value)
                if key == "spark.executor.cores":
                    spark_exectutor_cores = int(value)
                if key == "spark.driver.memory":
                    spark_driver_memory = int(value.replace("G", ""))
                if key == "spark.executor.memory":
                    spark_executor_memory = int(value.replace("G", ""))
                if key == "spark.dynamicAllocation.enabled":
                    dynamic_allocation = value
                if key == "spark.dynamicAllocation.maxExecutors":
                    max_executors = int(value.replace("G", ""))
                if key == "spark.dynamicAllocation.minExecutors":
                    min_executors = int(value.replace("G", ""))
            print(str.format("{} ({}) - Executor: {}g {} cores, Driver: {}g {} cores, Dynamic {}, Executors: min {} max {}", pipeline_count, title, spark_executor_memory, spark_exectutor_cores, spark_driver_memory, spark_driver_cores, dynamic_allocation, min_executors, max_executors))
            if max_executors == 0:
                item["value"].append({"key":"spark.dynamicAllocation.maxExecutors", "value": 3})
                commit["pipelineDefinition"] = json.dumps(pipeline_definition)

                # print(response.text)
                commit["commitId"] = commit_id

                #save the changest to teh draft 
                response = requests.post(str.format("https://cloud.streamsets.com/pipelinestore/rest/v1/pipelineCommit/{}", commit_id), headers=api_headers, json=commit)
                print(response.text)

                commit_message = "Updating max executors to 3, it was not set previously"
                # response = requests.post(str.format("https://cloud.streamsets.com/pipelinestore/rest/v1/pipelineCommit/{}/publish", commit_id), params={"commitMessage":commit_message}, headers=api_headers)
                
                quit()



print(str.format("{} - Executor: {}g {} cores, Driver: {}g {} cores", pipeline_count, spark_executor_memory, spark_exectutor_cores, spark_driver_memory, spark_driver_cores))