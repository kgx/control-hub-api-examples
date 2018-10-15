#!/usr/bin/env bash

#########################
## User properties to set
#########################

## Control Hub URL
SCH_URL=https://cloud.streamsets.com

## Data Collector Labels to swap
ACTIVE_LABEL=active
STANDBY_LABEL=standby

## Mode
MODE=DRY_RUN
#MODE=DO_IT

#########################
## End of user properties
#########################

## Control Hub Login URL
SCH_LOGIN_URL=$SCH_URL/security/public-rest/v1/authentication/login;

## Log in to Control Hub
curl -X POST -d @../private/sch_credentials.json $SCH_LOGIN_URL --header "Content-Type:application/json" --header "X-Requested-By:SDC" -c cookie.txt;

## Extract auth token from response
SESSION_TOKEN=$(cat cookie.txt | grep SSO | rev | grep -o '^\S*' | rev);

## Make sure we got an auth token
if [ -z $SESSION_TOKEN ]; 
  then
    echo "Error getting a new Control Hub Session Token";
    exit 1
  else
    rm cookie.txt
fi

## Call the python script to do the work
python ../python/migrate_jobs.py $SCH_URL $ACTIVE_LABEL $STANDBY_LABEL $SESSION_TOKEN $MODE
