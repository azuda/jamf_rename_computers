# https://developer.jamf.com/jamf-pro/docs/client-credentials
# https://developer.jamf.com/jamf-pro/reference/findcomputersbasic

from dotenv import load_dotenv
import os
import requests

# source .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
JAMF_URL = os.getenv("JAMF_URL")

def get_token():
  url = f"{JAMF_URL}/api/oauth/token"
  data = {
    "client_id": CLIENT_ID,
    "grant_type": "client_credentials",
    "client_secret": CLIENT_SECRET
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  response = requests.post(url, data=data, headers=headers, verify=False)
  response.raise_for_status()
  return response.json()["access_token"], response.json()["expires_in"]

def invalidate_token(token):
  url = f"{JAMF_URL}/api/v1/auth/invalidate-token"
  headers = {"Authorization": f"Bearer {token}"}
  response = requests.post(url, headers=headers, verify=False)
  if response.status_code == 204:
    print("Token successfully invalidated")
  elif response.status_code == 401:
    print("Token already invalid")
  else:
    print("An unknown error occurred invalidating the token")
