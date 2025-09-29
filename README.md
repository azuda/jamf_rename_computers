# usage

## improve this process

before running, add all computers you want to rename to the `Jamf computer rename` policy in jamf

1. run `query_jamf.py` to get list of computers

2. run `parse.py` to generate `all_computers.csv`

3. use excel to filter computers to rename

4. save filtered table to `rename.csv`

5. run `rename.py`

upon completion, all specified computers should now be correctly named `r-<username>` in jamf

> **Note:** this takes ~20 minutes to complete - do not drop network connection while running

correct name will get pushed to the device locally upon the next recurring check-in

## Quick Rename

`./quick_rename.sh <computer_id> <username>`
