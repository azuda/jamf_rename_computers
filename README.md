# Usage

before running, add all computers you want to rename to the `Jamf computer rename` policy in jamf

1. run `run.sh` to generate `all_computers.csv`

2. review all rows in `all_computers.csv` with `STATUS == CHECK`

3. update `STATUS` to `BAD` to rename; add computer id to `exceptions.csv` to skip

4. save .csv file(s)

5. run `rename.py`

upon completion, all specified computers should now be correctly named `r-<username>` in jamf

correct name will get pushed to the device locally upon the next recurring check-in

view most recent log in `logs/` for more details

> **Note:** this takes ~20 minutes to complete - do not drop network connection while running

## Quick Rename

`./quick_rename.sh <computer_id> <username>`

quick CLI method for renaming a single computer
