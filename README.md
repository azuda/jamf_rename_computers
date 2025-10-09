# README

## Setup

```sh
git clone https://github.com/azuda/jamf_computer_rename.git
cd jamf_computer_rename
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
gpg -do .env .env.gpg
```

## Usage
before running, add all computers you want to rename to the `Jamf computer rename` policy in jamf

1. run `run.sh`

2. review all rows in `all_computers.csv` with `STATUS == CHECK`

3. update `STATUS` to `BAD` to rename; add computer id to `exceptions.csv` to skip

4. save .csv file(s)

5. run `rename.py` to apply changes

upon completion, all computers that are assigned to a user should now be correctly named `r-<username>` in jamf

correct name will get pushed to the device locally upon the next recurring check-in

view most recent log in `logs/` for more details

> **Note:** this takes ~20 minutes to complete - do not drop network connection while running

## Info

- `run.sh` runs 3 scripts:
  - `query_jamf.py` gets all computers from jamf and saves to `response_computers_basic.json`
  - `parse.py` parses data `response_computers_basic.json` + adds userAndLocation info and saves to `all_computers.csv`
  - `rename.py` changes computer names based on criteria below and then saves updated entries to `all_computers.csv`

<details>
  <summary>computer rename criteria:</summary>

  - computer_id not in `exceptions.csv`
  - computer_name != r-&lt;UNAME&gt;
  - `STATUS` == `BAD`
  - assigned user email not empty
  > `STATUS` column is added by `parse.py`:
  > - if `COMPUTER_NAME` is equal to `r-<USERNAME>` and `id` is not in `exceptions.csv`, `STATUS` is set to `GOOD`
  > - if `COMPUTER_NAME` contains `<USERNAME>`, `STATUS` is set to `CHECK`
  > - if `COMPUTER_NAME` is not equal to `r-<USERNAME>` and `assigned user email` is not empty, `STATUS` is set to `BAD`
  > else `STATUS` is set to `UNASSIGNED`
</details>

## Quick Rename

quick CLI method for renaming a single computer

```sh
./quick_rename.sh <computer_id> <username>
```
