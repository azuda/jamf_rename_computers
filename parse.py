from jamf_credential import JAMF_URL, get_token, invalidate_token
import requests
import urllib3
import json
import csv
import time

with open("data/response_computers_basic.json") as f:
  data = json.load(f)
COMPUTERS = data.get("computers", [])

with open("data/exceptions.csv") as f:
  reader = csv.reader(f)
  EXCEPTIONS = [int(row[0]) for row in reader if row] # skip empty rows
print(f"Loaded {len(EXCEPTIONS)} exceptions from ./data/exceptions.csv")

# ==================================================================================

def add_user_data(computer_id, access_token, token_expiration_epoch):
  # renew token if expiration < 15 secs
  current_epoch = int(time.time())
  if current_epoch > token_expiration_epoch - 15:
    access_token, expires_in = get_token()
    token_expiration_epoch = current_epoch + expires_in
    print(f"Token valid for {expires_in} seconds")

  # GET userAndLocation by computer id
  user_url = f"{JAMF_URL}/api/v1/computers-inventory/{computer_id}?section=USER_AND_LOCATION"
  headers = {
    "accept": "application/json",
    "authorization": f"Bearer {access_token}"
  }
  response = requests.get(user_url, headers=headers, verify=False)
  # print(response.json())

  # add email, dept, building to computer
  email = response.json().get("userAndLocation", {"email": "N/A"}).get("email", "N/A")

  # convert dept id to dept name
  department_id = response.json().get("userAndLocation", {"departmentId": "N/A"}).get("departmentId", "N/A")
  try:
    response_dept = requests.get(f"{JAMF_URL}/JSSResource/departments/id/{department_id}", headers=headers, verify=False)
    department = response_dept.json().get("department", {"name": "N/A"}).get("name", "N/A")
  except:
    department = "N/A"

  # convert building id to building name
  building_id = response.json().get("userAndLocation", {"buildingId": "N/A"}).get("buildingId", "N/A")
  try:
    response_build = requests.get(f"{JAMF_URL}/JSSResource/buildings/id/{building_id}", headers=headers, verify=False)
    building = response_build.json().get("building", {"name": "N/A"}).get("name", "N/A")
  except:
    building = "N/A"

  # add cleaned user data to computer
  for computer in COMPUTERS:
    if computer["id"] == computer_id:
      computer["email"] = email
      computer["department"] = department
      computer["building"] = building
      print("Added userAndLocation for {:<8} {:<26} {}".format(computer['id'], computer['name'], computer['serial_number']))
      break

  return access_token, token_expiration_epoch

# ==================================================================================

def main():
  # initialize jamf api token
  access_token, expires_in = get_token()
  token_expiration_epoch = int(time.time()) + expires_in

  # add userAndLocation to computers where name is not r-username
  for computer in COMPUTERS:
    # if computer["name"] != f"r-{computer['username']}":
    #   access_token, token_expiration_epoch = add_user_data(
    #     computer["id"], access_token, token_expiration_epoch)
    access_token, token_expiration_epoch = add_user_data(
      computer["id"], access_token, token_expiration_epoch)
  invalidate_token(access_token)

  # filter useful keys
  for computer in COMPUTERS:
    keys_to_keep = ["id", "name", "serial_number", "username", "email", "department", "building", "STATUS", "UNAME"]
    for key in list(computer.keys()):
      if key not in keys_to_keep:
        del computer[key]
  print("Filtered useful columns")

  # populate STATUS + UNAME columns
  for computer in COMPUTERS:
    # if device has user assigned
    if isinstance(computer.get("username"), str) and isinstance(computer.get("email"), str) and computer["email"]:
      # disambiguate username
      uname = computer["email"].split("@")[0]
      computer["UNAME"] = uname
      if computer["name"] == f"r-{uname}" or computer["id"] in EXCEPTIONS: # ex. r-jsmith
        computer["STATUS"] = "GOOD"
      elif uname in computer["name"]: # ex. r-jsmith-m4
        computer["STATUS"] = "CHECK"
      else:
        computer["STATUS"] = "BAD"
    else:
      computer["STATUS"] = "Unassigned"
      computer["UNAME"] = "N/A"

  # write to csv
  with open("data/all_computers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=COMPUTERS[0].keys())
    writer.writeheader()
    writer.writerows(COMPUTERS)

  print("Done parse.py\n")

# ==================================================================================

if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  main()
