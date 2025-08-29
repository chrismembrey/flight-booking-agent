import requests
import os
from dotenv import load_dotenv, find_dotenv
from utils.amadeus_auth import get_amadeus_access_token

load_dotenv(find_dotenv())

def confirm_flight_price(raw_offer):
    url = f"{os.getenv('AMADEUS_BASE_URL')}/v1/shopping/flight-offers/pricing"
    token = get_amadeus_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.amadeus+json",
        "X-HTTP-Method-Override": "GET"
    }
    body = {
        "data": {
            "type": "flight-offers-pricing",
            "flightOffers": [raw_offer]
        }
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()