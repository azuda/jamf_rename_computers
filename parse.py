from jamf_credential import JAMF_URL, get_token, invalidate_token
import requests
import urllib3
import json
import csv

with open("data/response_computers_basic.json") as f:
  data = json.load(f)
COMPUTERS = data.get("computers", [])

# with open("data/response_computers_user.json") as f:
#   data = json.load(f)
# COMPUTERS_USERS = {comp["id"]: comp for comp in data.get("computers", [])}

# add email to COMPUTERS and convert to csv

# ==================================================================================

def add_email(computer_id):
  # create access token
  access_token, expires_in = get_token()
  print(f"Token valid for {expires_in} seconds")

  user_url = f"{JAMF_URL}/api/v1/computers-inventory/{computer_id}?section=USER_AND_LOCATION"
  headers = {
    "accept": "application/json",
    "authorization": f"Bearer {access_token}"
  }
  response = requests.get(user_url, headers=headers, verify=False)

  with open("data/templookatthis.json", "w") as f:
    json.dump(response.json(), f)

  # kill access token
  invalidate_token(access_token)

# ==================================================================================

def main():
  for computer in COMPUTERS:
    if computer["name"] != f"r-{computer["username"]}":
      print(f"Adding email for {computer}")
      add_email(computer["id"])
      break

  print("Done parse.py")

if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  main()
