from jamf_credential import JAMF_URL, get_token, invalidate_token
import requests
import urllib3
import csv
import time
import os
import sys
from datetime import datetime

with open("data/all_computers.csv", "r") as f:
  reader = csv.DictReader(f)
  COMPUTERS = [row for row in reader]

# find most recent log file
# log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
# if log_files:
#   log_files.sort(key=lambda x: os.path.getmtime(os.path.join("logs", x)), reverse=True)
#   LOG_FILE = os.path.join("logs", log_files[0])
#   print(f"Log file: {LOG_FILE}")

# ==================================================================================

def rename_computer(computer, computer_id, new_name, access_token, token_expiration_epoch):
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
    # update computer entry
    computer["name"] = new_name
    computer["STATUS"] = "GOOD"
  else:
    print(f"{response.status_code} Failed to rename computer {computer_id}:\n{response.text}")

  return access_token, token_expiration_epoch

# def log(message):
#   print(message)
#   with open(LOG_FILE, "a") as f:
#     f.write(f"{message}\n")
#   f.close()
#   return

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
        computer, computer["id"], f"r-{computer['UNAME']}", access_token, token_expiration_epoch)
  invalidate_token(access_token)

  # write renamed computer entries back to csv
  with open("data/all_computers.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=COMPUTERS[0].keys())
    writer.writeheader()
    writer.writerows(COMPUTERS)
  f.close()

  print("Done rename.py")

# ==================================================================================

if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  main()
