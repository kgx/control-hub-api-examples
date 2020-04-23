# Testing that best practices are used in a Pipeline

This example retrieves the latest commit (i.e. version) of a given pipeline, and verifies it for best practices.  Only one best practice is implemented right now (adding descriptive labels)

## Prerequisites

* An account on StreamSets Control Hub with read and write permissions on Jobs and Pipelines
* A Python 3 environment

## Step 1: Start with a Pipeline Version like this:

On the Info tab you can see the Pipeline ID:

![pipeline3](images/pipeline3.png) 

## Step 2: Provide Control Hub credentials 

Set your Control Hub credentials in the file ```private/sch_credentials.json```
  
## Step 3: Prepare the script
 
Set the Control Hub URL and Pipeline ID in the script ```bin/create_job_for_pipeline.sh```.
That script is a wrapper around the python script located at ```python/create_job_for_pipeline.py```
  
## Step 4: Run the script
 
To run the script, cd to the bin directory and execute the command ```./create_job_for_pipeline.sh```:

Here is an example session:
 
```
** Runtime Parameters ********************
REPLICA_ORIGIN_TABLE : COURSEOFFERING
REPLICA_SNOWFLAKE_ACCOUNT : k12
REPLICA_SNOWFLAKE_USER : PIPELINE_USER_DEV
REPLICA_SNOWFLAKE_PASSWORD : devPipelinek12pass
REPLICA_SNOWFLAKE_WAREHOUSE : LOAD_WH
REPLICA_ORIGIN_SCHEMA : REPLICA_DEV10_SAMS
REPLICA_ORIGIN_DATABASE : DATAVAULT_DEV
REPLICA_ORIGIN_TABLE_COLUMNS : ID,SCHOOLYEAR,MODIFYDATE,IS_DELETED,VLT_CREATE_DATETIME
STG_SNOWFLAKE_ACCOUNT : k12
STG_SNOWFLAKE_USER : PIPELINE_USER_DEV
STG_SNOWFLAKE_PASSWORD : devPipelinek12pass
STG_SNOWFLAKE_WAREHOUSE : LOAD_WH
STG_DEST_TABLE : STG_CLASSROOM_OFFERING_ACADEMIC_YEAR_SAMS
STG_DEST_DATABASE : DATAVAULT_DEV
STG_DEST_SCHEMA : STAGE_DEV_10_SAMS
Testing Job
Detected non-descriptive label: Replica Origin Read Mode As Query - Fragment 1
Detected non-descriptive label: Field Renamer
Detected non-descriptive label: Type Converter
Detected non-descriptive label: Staging Destination Fragment 1
```
 
