#!/usr/bin/env python

###################################################################################################
##
## data_usage_report.py
##
## Generates a report of data sources accessed by SteamSets Jobs 
## within the given start and end dates 
##
## Usage: python data_usage_report.py <sch_url> <start_date> <end_date> <output_file> <sch_session_token>'
##
## Example: python data_usage_report.py http://localhost:18631 2018-01-01 2018-01-31 /tmp/data-access-report.tsv $SESSION_TOKEN'
##
## Start Date and End Date args should be formatted as yyyy-mm-dd
##
####################################################################################################

## Imports
import datetime
import json
import requests
import sys
import data_source_config

## Delimiter for output file
delimiter = '|'

## Command line args
if len(sys.argv) != 6:
  print ('Error: Wrong number of arguments')
  print ('Usage: python data_usage_report.py <sch_url> <start_date> <end_date> <output_file> <sch_session_token>')
  quit(1)

sch_url = sys.argv[1];
start_date = sys.argv[2]
end_date = sys.argv[3]
output_file = sys.argv[4]
session_token = sys.argv[5]

print('\n')
print('================================================')
print ('Data Access Report from ' + start_date + ' to ' + end_date)
print('================================================\n')

###############################
## Common headers for API calls
###############################
api_headers = {}
api_headers['Content-type'] = 'application/json'
api_headers['X-Requested-By'] = 'SDC'
api_headers['X-SS-REST-CALL'] = 'true'
api_headers['X-SS-User-Auth-Token'] = session_token

########################################
## Convert Start and End dates to millis
########################################
start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
start_date_millis = start_date_dt.timestamp() * 1000

end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
end_date_millis = end_date_dt.timestamp() * 1000

if end_date_millis <= start_date_millis:
  print('Error: End Date should be greater than Start Date')
  exit (-1)

##############################
## Column Names for the report
##############################
column_names = []
column_names.append('Job Name')
column_names.append('Pipeline Name')
column_names.append('Pipeline Version')
column_names.append('Last Run Date')
column_names.append('User')
column_names.append('Data Source')
column_names.append('Config 1 Name')
column_names.append('Config 1 Value')
column_names.append('Config 2 Name')
column_names.append('Config 2 Value')
column_names.append('Config 3 Name')
column_names.append('Config 3 Value')

## We'll store report data here and print it at the end
report_data = []

########################################
## Get the list of Jobs from Control Hub
########################################
endpoint_url = sch_url + '/jobrunner/rest/v1/jobs'
response = requests.get( url = endpoint_url, headers = api_headers )
if response.status_code != 200: 
  print('Error getting job list')
  print(response.status_code)
  print(response.text)
  exit (-1)
jobs = response.json()

##################
## For each job... 
##################
for job in jobs:

  ## Make sure the job has been run at least once
  if  job['currentJobStatus'] != None:
  
    ## Include only jobs run between the start date and end date
    job_start_time_millis = job['currentJobStatus']['startTime']
    if job_start_time_millis >= start_date_millis and job_start_time_millis <= end_date_millis:

      ## Create a dictionary to hold values for a report line
      report_values = {}
      
      ## Append report values to the line
      report_values['Job Name'] = job['name']
      report_values['Pipeline Name'] = job['pipelineName']
      report_values['Pipeline Version'] = job['pipelineCommitLabel']
      last_run_date = datetime.datetime.fromtimestamp(float(job_start_time_millis)/1000).strftime('%Y-%m-%d %H:%M:%S')
      report_values['Last Run Date'] = last_run_date
      report_values['User'] = job['currentJobStatus']['user']

      ## Get the Job's Parameters
      job_parameters_string = job['runtimeParameters']
      if job_parameters_string is not None:
        parameters = json.loads(job['runtimeParameters'])
      else:
        parameters = {}
      
      ## Get the Pipeline Commit to find the Data Source and pipeline parameter values
      endpoint_url = sch_url + '/pipelinestore/rest/v1/pipelineCommit/' + job['pipelineCommitId']
      pipeline_commit_response = requests.get( url = endpoint_url, headers = api_headers )
      if pipeline_commit_response.status_code != 200: 
        print('Error getting pipeline commit')
        print(pipeline_commit_response.status_code)
        print(pipeline_commit_response.text)
        exit (-1)
    
      ## Get the Pipeline Definition 
      pipeline_definition = json.loads(pipeline_commit_response.json()['pipelineDefinition'])
      
      ## Get the Pipeline Configuration 
      configuration = pipeline_definition['configuration']
      
      ## Get Pipeline Parameters
      pipeline_parameters = {}
      for item in configuration:
        if item['name'] == 'constants':
          for param in item['value']:
            pipeline_parameters[param['key']] = param['value']
          break

      ## Get the data source (the Origin)
      origin = pipeline_definition['stages'][0]
      data_source = origin['stageName']
      
      ## See if we have a config for this data source type in the file python/data_source_config.py
      if data_source in data_source_config.data_sources.keys():
      
        ## Get label from data source config
        data_source_label = data_source_config.data_sources[data_source]['label']
        
        ## Get properties from data source config
        properties_for_report = {}
        data_source_config_properties = data_source_config.data_sources[data_source]['properties']
        
        for prop in data_source_config_properties.keys():

          ##  We'll set this to true it we find the property in the origin's config
          prop_found = False

          ## If the prop does not contains a "/", we'll look for a top level value
          if not '/' in prop:
            prop_label = data_source_config_properties[prop]
            for item in origin['configuration']:
              if item['name'] == prop:
                prop_value = item['value']
                prop_found = True
                break

          else: ## The prop contains a "/", so we'll look for a nested value

            ## Split the nested property
            ## An example nested property is "tableJdbcConfigBean.tableConfigs/tablePattern"
            nested_prop = prop.split('/')
            if len(nested_prop) > 2:
              print('Error handling the config property \'' + prop + '\'') 
              print ('This program can\'t handle more than one level of nested properties')
              print('Aborting report')
              exit(-1)

            for item in origin['configuration']:
              if item['name'] == nested_prop[0]:
                for key in item['value'][0].keys():
                  if key == nested_prop[1]:
                    prop_label = data_source_config_properties[prop]
                    prop_value = item['value'][0][nested_prop[1]]
                    prop_found = True
                    break

          if isinstance(prop_value, str):
            properties_for_report[prop_label] = prop_value
          elif isinstance(prop_value, list):
            properties_for_report[prop_label] = ', '.join(prop_value)
          else:
            print('Error: Config property value is not a String or a List.')
            print('Value is ' + prop_value + 'type is ' + type(prop_value))
            print('Aborting report')
            exit(-1)

          if not prop_found:    
            print('Error: config property \'' + prop + '\' not found for data source \'' + data_source + '\'\n')
            print('Aborting report')
            exit(-1)
               
        ## Replace property values with parameter values if they are parameterized
        for prop in properties_for_report:
          value = properties_for_report[prop]
          ## If value is a parameter (i.e. "${...}")
          if value.startswith('${') and value.endswith('}'):
            parameter_key = value[2:-1]
            parameter_value = None
            if parameter_key in parameters:
              parameter_value = parameters[parameter_key]
            
            ## If we found a parameter value
            if parameter_value is not None and len(parameter_value) > 0:
            
              ## Replace the config value with the parameter value
              properties_for_report[prop] = parameter_value

            else:

              ## Get the parameter value from the Pipeline rather than the Job
              properties_for_report[prop] =  pipeline_parameters[parameter_key]

      else:
        ## If we don't have a config for this data source use the stage lib 
        ##  name as the data source and don't retrieve any properties
        data_source_label = data_source
        properties_for_report = {}

      report_values['Data Source'] = data_source_label

      ## Append a maximum of three config properties (a limit of this version of the report)
      counter = 1
      for prop in properties_for_report:
        if counter < 4:
          report_values['Config ' + str(counter ) + ' Name'] = prop
          report_values['Config ' + str(counter) + ' Value']  = properties_for_report[prop]
          counter = counter + 1
        else:
          break
          
      ## Store the report data
      report_data.append(report_values)
      
      ## Write each line to the screen:
      print('=======================================')
      for key in report_values.keys():
        print(key + ': ' + report_values[key])

print('=======================================')


####################
## Create the Report
####################

## Open a file for the report
with open(output_file,'w') as report:

  ## Write the header line
  header_line = delimiter.join(column_names)
  report.write(header_line + '\n')

  ## Write the report lines
  for data in report_data:
    line_data = []
    for column_name in column_names:
      if column_name in data.keys():
        line_data.append(data[column_name])
    report_line = delimiter.join(line_data)
    report.write(report_line + '\n') 

print('\nCreated Data Access Report in the file ' + output_file)
print('\nDone')  
