from jamf_credential import JAMF_URL, get_token, invalidate_token
import requests
import urllib3
import csv
import time
import os
import sys

with open("data/all_computers.csv", "r") as f:
  reader = csv.DictReader(f)
  COMPUTERS = [row for row in reader]

# append logs to log file via LOG_FILE env var
log_file = os.environ.get("LOG_FILE")
if log_file:
  log_output = open(log_file, "a")
  sys.stdout = log_output
  sys.stderr = log_output

# ==================================================================================

def rename_computer(computer_id, new_name, access_token, token_expiration_epoch):
  # renew token if expiration < 15 secs
  current_epoch = int(time.time())
  if current_epoch > token_expiration_epoch - 15:
    access_token, expires_in = get_token()
    token_expiration_epoch = current_epoch + expires_in

  rename_url = f"{JAMF_URL}/api/v1/computers-inventory-detail/{computer_id}"
  headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {access_token}"
  }
  payload = {"general": {"name": new_name}}
  response = requests.patch(rename_url, headers=headers, json=payload, verify=False)

  if response.status_code == 200:
    print(f"Successfully renamed computer {computer_id} to {new_name}")
  else:
    print(f"{response.status_code} Failed to rename computer {computer_id}:\n{response.text}")

  return access_token, token_expiration_epoch

# ==================================================================================

def main():
  # initialize jamf api token
  access_token, expires_in = get_token()
  token_expiration_epoch = int(time.time()) + expires_in

  # rename computers
  for computer in COMPUTERS:
    if computer["STATUS"] == "BAD":
      print(f"Renaming computer {computer['serial_number']} - {computer['name']} to r-{computer['UNAME']}")
      access_token, token_expiration_epoch = rename_computer(
        computer["id"], f"r-{computer['UNAME']}", access_token, token_expiration_epoch)
  invalidate_token(access_token)

  print("Done rename.py\n")

# ==================================================================================

if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  main()
