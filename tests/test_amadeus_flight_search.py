import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load .env variables
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

def test_flight_search():
    token = get_amadeus_access_token()
    url = f"{os.getenv('AMADEUS_BASE_URL')}/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
  'originLocationCode': 'LHR',
  'destinationLocationCode': 'JFK',
  'departureDate': '2025-10-15',
  'returnDate': '2025-10-20',
  'adults': 1,
  'travelClass': 'ECONOMY',
  'nonStop': 'true', 
  'currencyCode': 'GBP',
  'max': 20
}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    results = response.json()
    print(f"Returned {len(results.get('data', []))} flight offers.")
    for offer in results.get("data", [])[:2]:
        print("Price:", offer["price"]["total"])
        for itinerary in offer["itineraries"]:
            for seg in itinerary["segments"]:
                print(f"  {seg['departure']['iataCode']} → {seg['arrival']['iataCode']} @ {seg['departure']['at']}")

if __name__ == "__main__":
    test_flight_search()