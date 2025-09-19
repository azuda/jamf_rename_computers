import json, csv


with open('data/response_jamf_computers.json', 'r') as f:
  data = json.load(f)
COMPUTERS = data.get('results', [])

with open('data/response_jamf_computer_users.json', 'r') as f:
  data = json.load(f)
data_users = {}
for computer in data.get('results', []):
  data_users[computer['id']] = computer
COMPUTER_USERS = data_users

with open('data/response_jamf_departments.json', 'r') as f:
  data = json.load(f)
DEPARTMENTS = data.get('results', [])


def get_user_data(computer_id):
  if computer_id in COMPUTER_USERS:
    return COMPUTER_USERS[computer_id]['userAndLocation']
  return None


def parse_department(department_id):
  for department in DEPARTMENTS:
    if department['id'] == department_id:
      return department['name']
  return None


def main():
  output = []
  for computer in COMPUTERS:
    current = {}
    current['id'] = computer['id']
    current['sn'] = computer.get('hardware', {}).get('serialNumber', 'Unknown')
    current['username'] = None
    current['full_name'] = None
    current['email'] = None
    current['egy'] = None
    current['department'] = None
    current['building'] = None

    user_data = get_user_data(computer.get('id'))
    if user_data:
      current['username'] = user_data['username']
      current['full_name'] = user_data['realname']
      current['email'] = user_data['email']
      current['egy'] = user_data['position']
      current['department'] = parse_department(user_data['departmentId'])
      current['building'] = user_data['buildingId']

    output.append(current)

  # Write to CSV
  with open('ALL_COMPUTERS.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=output[0].keys())
    writer.writeheader()
    writer.writerows(output)
  print('Generated ALL_COMPUTERS.csv')


if __name__ == '__main__':
  print('\nStart')

  main()

  print('Done')
