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
import sqlparse


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

endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelines?onlyPublished=true&executionModes=STREAMING&orderBy=LAST_MODIFIED_ON&order=DESC'
response = requests.get( url = endpoint_url, headers = api_headers)
# print(response.text)
pipelines = json.loads(response.text)["data"]
for pipeline in pipelines:
    pipeline_id = pipeline["pipelineId"]
    commit_id = pipeline["commitId"]

    ## Set the pipeline_id as the payload
    payload = [pipeline_id]

    ## Call the API 
    endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelines/latestCommit'
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

    print('\n\n**************************************************')
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
    # print('Getting runtime parameters for commit ID: ' + latest_commit['commitId'] + '\n')

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
    #print("pipelineDefinition: {}", pipeline_definition)

    configuration = pipeline_definition['configuration']
    for item in configuration:
        if item['name'] == 'constants':
            for param in item['value']:
                value = param["value"]
                key = param['key']
                runtime_parameters[key] = value
                if "$" in value and "runtime:loadResource" not in value: 
                    print("Detected non loadResource configuration, which disables changes at runtime in " + key + ' : ' + value)
            break


    ###############
    ## Create a Job
    ###############
    print('Testing for best practices: ')

    stages = pipeline_definition['stages']
    for stage in stages: 
        label = stage["uiInfo"]["label"]
        clean_label = re.sub(r"[\s\d_-]","",label)
        instance_name = re.sub("_.*","",stage["instanceName"])
        #print("checking stage " + instance_name + "(" + clean_label + ")")
        if re.match(r".*\d$", label) or clean_label == instance_name:
            print("Detected non-descriptive label: " + label)

        if stage["library"] == "streamsets-spark-snowflake-lib":
            configuration = stage['configuration']
            for item in configuration:
                #print(item['name'] + " " + str(item["value"]))
                value = item["value"]
                if item['name'] == 'conf.readMode' and value != "QUERY":
                    print("Detected non-query mode Snowflake Origin: " + label + " this will not enable query push-down")
                if item['name'] == 'conf.query':
                    parsed = sqlparse.parse(value)[0]
                    prior_token = parsed.tokens[0]
                    for token in parsed.tokens:
                        #print(str(token.ttype) + " " + str(token))
                        if prior_token.match(sqlparse.tokens.Keyword, ["JOIN", "FROM"], regex=False) and token.match(None, "[^\$\.\s]*", regex=True):
                            #print(str(token.ttype) + " " + str(token))
                            print("Detected non-fully qualified table in query " + label + " which could cause issues with push-down: " + value)
                        if token.match(sqlparse.tokens.Keyword, ["JOIN", "FROM"], regex=False):
                            #print(str(token.ttype) + " " + str(token))
                            prior_token = token



    # Other things to check from API: 
    # 1. Hard coding of databases / schemas in fragments
    # 2. Check for empty batches ahead of field renamer
    # 3. loadResource instead of conf
    # 4. LOAD_DATE CURRENT_TIME in an expression
    # 5. LOAD_DATE not renamed from the source to the LOAD_DATE ()

    # Things to ccheck using Streamsets Test Framework
    # 1. Required Data Vault columns (HKEYS, LOAD_DATE, etc.) are present on all data frames that would be loaded into Raw Vault Tables

