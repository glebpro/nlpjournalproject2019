
# check for needed input
if [ -z "$API_KEY" ]
then
  echo 'set api key with: `export API_KEY=KEY`'
  exit 1
fi
if [ -z "$URL" ]
then
  echo 'set URL with: `export URL=URL`'
  exit 1
fi
if [ -z "$(which jq)" ]
then
  echo 'install jq: `brew install jq`'
  exit 1
fi

# setup enviornment and get environment_id
environment_id=`curl -X POST -u "apikey:$API_KEY" -H "Content-Type: application/json" -d "{\"name\":\"hindsight-environment\", \"description\":\"the hindsight app env\"}" "$URL/v1/environments?version=2018-12-03" | jq -r '.environment_id'`

# wait until it's setup
curr_status="0"
while [ "$curr_status" != "active" ]
do
  curr_status=`curl -u "apikey:$API_KEY" "$URL/v1/environments/$environment_id?version=2018-12-03" | jq -r '.status'`
  sleep 5
done

# get default config, use to create collection
default_configuration_id=`curl -u "apikey:$API_KEY" "$URL/v1/environments/$environment_id/configurations?version=2018-12-03" | jq -r '.configurations[0].configuration_id'`
hindsight_collection_id=`curl -X POST -u "apikey:$API_KEY" -H "Content-Type: application/json" -d "{\"name\": \"hindsight-collection\", \"description\": \"collection of docs for hindsight\", \"configuration_id\":\"$default_configuration_id\" , \"language\": \"en_us\"}" "$URL/v1/environments/$environment_id/collections?version=2018-12-03" | jq -r '.collection_id'`

# wait till done
curr_status="0"
while [ "$curr_status" != "active" ]
do
  curr_status=`curl -u "apikey:$API_KEY" "$URL/v1/environments/$environment_id/collections/$hindsight_collection_id?version=2018-12-03" | jq -r '.status'`
  sleep 5
done

echo "IBM Enviornment setup..."
echo "EnviornmentID: $environment_id"
echo "CollectionID: $hindsight_collection_id"
