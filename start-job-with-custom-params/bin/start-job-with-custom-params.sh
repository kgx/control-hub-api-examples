#!/usr/bin/env bash

#########################
## User properties to set
#########################

## Control Hub URL
SCH_URL=https://cloud.streamsets.com

## Job ID
JOB_ID=db26385e-2cf2-4e63-a52b-61369396cdc9:globex

## Custom Parameter Values
PARAMS='{"OUTPUT_DIR":"/tmp/out/dir100","FILE_PREFIX":"mark_100_"}'

#########################
## End of user properties
#########################

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
python ../python/start_job_with_custom_params.py $SCH_URL $JOB_ID $PARAMS $SESSION_TOKEN
