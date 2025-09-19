#!/bin/sh

# https://developer.jamf.com/jamf-pro/docs/client-credentials

# read csv of computers we want to rename
# rename computer using jamf api

source "./.env"
url=$JAMF_URL
client_id=$CLIENT_ID
client_secret=$CLIENT_SECRET

getAccessToken() {
  response=$(curl --silent --location --request POST "${url}/api/oauth/token" \
    --header "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "client_id=${client_id}" \
    --data-urlencode "grant_type=client_credentials" \
    --data-urlencode "client_secret=${client_secret}")
  access_token=$(echo "$response" | plutil -extract access_token raw -)
  token_expires_in=$(echo "$response" | plutil -extract expires_in raw -)
  token_expiration_epoch=$(($current_epoch + $token_expires_in - 1))
}

checkTokenExpiration() {
  current_epoch=$(date +%s)
    if [[ token_expiration_epoch -ge current_epoch ]]
    then
      printf "\nToken valid until $(date -r $token_expiration_epoch '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    else
      printf "\nNo valid token available, getting new token" >> "$LOG_FILE" 2>&1
      getAccessToken
    fi
}

invalidateToken() {
  responseCode=$(curl -w "%{http_code}" -H "Authorization: Bearer ${access_token}" $url/api/v1/auth/invalidate-token -X POST -s -o /dev/null)
  if [[ ${responseCode} == 204 ]]
  then
    printf "\nToken successfully invalidated" >> "$LOG_FILE" 2>&1
    access_token=""
    token_expiration_epoch="0"
  elif [[ ${responseCode} == 401 ]]
  then
    printf "\nToken already invalid" >> "$LOG_FILE" 2>&1
  else
    printf "\nAn unknown error occurred invalidating the token" >> "$LOG_FILE" 2>&1
  fi
}

renameComputer() {
  local jamf_id="$1"
  local username="$2"
  payload=$(printf '{"general": {"name": "r-%s"}}' "$username")
  response=$(
    curl -X 'PATCH' \
    "$JAMF_URL/api/v1/computers-inventory-detail/$jamf_id" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $access_token" \
    -d "$payload"
  )
  echo "$response" > "./data/raw.json"
  tr -d "\11\12\15\40-\176" < ./data/raw.json > ./data/cleaned.json  
  http_status=$(cat ./data/cleaned.json | jq -r '.httpStatus // empty')
  if [[ "$http_status" -ge 400 && "$http_status" -le 499 ]]; then
    printf "\nFailed to rename computer r-%s" "$username" >> "$LOG_FILE" 2>&1
    printf "\nResponse: %s\n" "$response" >> "$LOG_FILE" 2>&1
  else
    printf "\nSuccessfully renamed computer r-%s" "$username" >> "$LOG_FILE" 2>&1
  fi
}

# log output
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/$(date '+%Y-%m-%d_%H-%M-%S').log"
mkdir -p "$LOG_DIR"
ls -1t "$LOG_DIR" | tail -n +5 | xargs -I {} rm -f "$LOG_DIR/{}"

printf "Start @ $(date -r $(date +%s) '+%Y-%m-%d %H:%M:%S')"  >> "$LOG_FILE" 2>&1

FILENAME="rename.csv" # format as 2 columns: [ids,  usernames], no headers
if [ ! -f "$FILENAME" ]; then
  echo "File $FILENAME does not exist, exiting"
  exit 1
fi
echo "File $FILENAME exists"
/opt/homebrew/bin/dos2unix "$FILENAME"
cat "$FILENAME"

# create api access token
# checkTokenExpiration
# curl -H "Authorization: Bearer $access_token" $url/api/v1/jamf-pro-version -X GET
# checkTokenExpiration

# loop through and rename computers
count=0
printf "\nEntering rename loop..." >> "$LOG_FILE" 2>&1
while IFS=',' read -r id username; do
  id=$(echo "$id" | tr -d '\r' | xargs)
  username=$(echo "$username" | tr -d '\r' | xargs)
  # echo "Read line: id='$id', username='$username'"
  printf "\n" >> "$LOG_FILE" 2>&1
  if [ -n "$id" ] && [ -n "$username" ]; then
    checkTokenExpiration
    printf "\nCalling renameComputer on id=$id, username=$username @ $(date -r $(date +%s) '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    renameComputer "$id" "$username"
    count=$((count + 1))
  else
    printf "\nSkipping computer $id due to missing id or username" >> "$LOG_FILE" 2>&1
  fi
done < "$FILENAME"
printf "\n\nProcessed $count computers" >> "$LOG_FILE" 2>&1

# kill api access token
invalidateToken
curl -H "Authorization: Bearer $access_token" $url/api/v1/jamf-pro-version -X GET
printf "\nDone @ $(date -r $(date +%s) '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
