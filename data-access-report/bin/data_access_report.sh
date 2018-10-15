#!/usr/bin/env bash

###################################
## Properties to set for the report
###################################
## Control Hub URL
SCH_URL=https://cloud.streamsets.com

## Report Start Date YYYY-MM-DD
START_DATE=2018-01-01

## Report End Date YYYY-MM-DD
END_DATE=2018-12-31

## Output File
OUTPUT_FILE=~/data-access-report-2018-09-08.txt
##########################################
## End of properties to set for the report
##########################################

## Control Hub Login URL
SCH_LOGIN_URL=$SCH_URL/security/public-rest/v1/authentication/login;

## Log in to Control Hub
curl -X POST -d @../private/sch_credentials.json $SCH_LOGIN_URL --header "Content-Type:application/json" --header "X-Requested-By:SDC" -c cookie.txt;

## Extract auth token from response
SESSION_TOKEN=$(cat cookie.txt | grep SSO | rev | grep -o '^\S*' | rev);
rm cookie.txt;

## Make sure we got an auth token
if [ -z $SESSION_TOKEN ]; 
  then
    echo "Error getting a new Control Hub Session Token";
    exit 1
fi

## Call the python script to do the work    
python ../python/data_access_report.py $SCH_URL $START_DATE $END_DATE $OUTPUT_FILE $SESSION_TOKEN



