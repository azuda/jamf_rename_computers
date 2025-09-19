# usage

before running the scripts, add all computers you want to rename to the `Jamf computer rename` policy in Jamf Pro

1. run `query_jamf.sh` to generate `ALL_COMPUTERS.csv`

2. use excel tables to filter computers you want from `ALL_COMPUTERS.csv`

3. copy **id** and **username** columns to a new file named `rename.csv` (do not include table headers)

4. run `rename_computers.sh`

upon completion, all specified computers should now be correctly named `r-<username>` in jamf

correct name will get pushed to the device locally the next time policy is applied / upon check-in
