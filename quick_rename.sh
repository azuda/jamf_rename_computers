#!/bin/sh

# https://developer.jamf.com/jamf-pro/docs/client-credentials

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <jamf_id> <username>"
  exit 1
fi

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

LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/QR-$(date '+%Y-%m-%d_%H-%M-%S').log"
mkdir -p "$LOG_DIR"
ls -1t "$LOG_DIR" | tail -n +5 | xargs -I {} rm -f "$LOG_DIR/{}"

jamf_id=$(echo "$1" | tr -d '\r' | xargs)
username=$(echo "$2" | tr -d '\r' | xargs)

printf "Start @ $(date -r $(date +%s) '+%Y-%m-%d %H:%M:%S')"  >> "$LOG_FILE" 2>&1

checkTokenExpiration
printf "\nCalling renameComputer on id=$jamf_id, username=$username @ $(date -r $(date +%s) '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
renameComputer "$jamf_id" "$username" >> "$LOG_FILE" 2>&1

invalidateToken
printf "\nDone @ $(date -r $(date +%s) '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
