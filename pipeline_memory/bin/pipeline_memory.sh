## Control Hub URL
export SCH_URL=https://cloud.streamsets.com

## Pipeline ID
export PIPELINE_ID=bf9c754e-3c55-4b16-b051-04f083f365e2:dpmfield

##########################
## No changes needed below
##########################
 
## Control Hub Login URL
export SCH_LOGIN_URL=$SCH_URL/security/public-rest/v1/authentication/login;

## Log in to Control Hub
curl -X POST -d @../private/sch_credentials.json $SCH_LOGIN_URL --header "Content-Type:application/json" --header "X-Requested-By:SDC" -c cookie.txt;

## Extract auth token from response
export SESSION_TOKEN=$(cat cookie.txt | grep SSO | rev | grep -o '^\S*' | rev);