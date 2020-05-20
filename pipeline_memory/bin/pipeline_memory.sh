## Control Hub URL
export SCH_URL=https://cloud.streamsets.com


##########################
## No changes needed below
##########################

## Control Hub Login URL
export SCH_LOGIN_URL=$SCH_URL/security/public-rest/v1/authentication/login;

## Log in to Control Hub
curl -X POST -d @./private/sch_credentials.json $SCH_LOGIN_URL --header "Content-Type:application/json" --header "X-Requested-By:SDC" -c cookie.txt;

## Extract auth token from response
export SESSION_TOKEN=$(cat cookie.txt | grep SSO | rev | grep -o '^\S*' | rev);

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
python3 ./python/pipeline_memory.py $SCH_URL $SESSION_TOKEN 