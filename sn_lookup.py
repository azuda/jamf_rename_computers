import csv

with open('serial_numbers.csv', 'r') as f:
  reader = csv.reader(f)
  SERIAL_NUMBERS = [row[0] for row in reader]

with open('ALL_COMPUTERS.csv', 'r') as f:
  reader = csv.DictReader(f)
  COMPUTERS = {row['sn']: row for row in reader}

result = []
for sn in SERIAL_NUMBERS:
  if sn in COMPUTERS:
    result.append(COMPUTERS[sn])

with open('sn_lookup_output.csv', 'w') as f:
  writer = csv.DictWriter(f, fieldnames=result[0].keys())
  writer.writeheader()
  writer.writerows(result)
