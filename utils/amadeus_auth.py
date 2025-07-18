import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_amadeus_access_token():
    url = f"{os.getenv('AMADEUS_BASE_URL')}/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AMADEUS_API_KEY"),
        "client_secret": os.getenv("AMADEUS_SECRET_KEY")
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]