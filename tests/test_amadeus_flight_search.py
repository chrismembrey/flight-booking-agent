import os
import requests
from collections import Counter
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

def test_flight_search_and_pricing():
    token = get_amadeus_access_token()
    url = f"{os.getenv('AMADEUS_BASE_URL')}/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        'originLocationCode': 'LHR',
        'destinationLocationCode': 'JFK',
        'departureDate': '2025-12-15',
        'returnDate': '2025-12-20',
        'adults': 1,
        'travelClass': 'ECONOMY',
        'nonStop': 'true',
        'currencyCode': 'GBP',
        'max': 200
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    results = response.json()

    offers = results.get("data", [])
    print(f"\n✅ {len(offers)} flight offers returned.\n")

    carrier_counter = Counter()
    validating_counter = Counter()

    selected_offer = offers[0] if offers else None

    for idx, offer in enumerate(offers):
        price = offer.get("price", {}).get("total", "N/A")
        validating_airlines = offer.get("validatingAirlineCodes", [])
        print(f"\U0001F4B0 Price: {price} | Validating: {', '.join(validating_airlines)}")
        validating_counter.update(validating_airlines)

        for itinerary in offer.get("itineraries", []):
            for seg in itinerary.get("segments", []):
                dep = seg["departure"]["iataCode"]
                arr = seg["arrival"]["iataCode"]
                dep_time = seg["departure"]["at"]
                carrier = seg["carrierCode"]
                op_carrier = seg.get("operating", {}).get("carrierCode", carrier)

                print(f"  ✈ {dep} → {arr} @ {dep_time} | Carrier: {carrier} | Operated by: {op_carrier}")
                carrier_counter.update([op_carrier])

        print("-" * 60)

    print("\n📊 Carrier breakdown (operating airlines):")
    for carrier, count in carrier_counter.items():
        print(f"  - {carrier}: {count} segments")

    print("\n📦 Validating airline codes:")
    for val_airline, count in validating_counter.items():
        print(f"  - {val_airline}: {count} offers")

    if selected_offer:
        print("\n🔎 Confirming price for first flight offer...")
        pricing_url = f"{os.getenv('AMADEUS_BASE_URL')}/v1/shopping/flight-offers/pricing"
        pricing_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.amadeus+json"
        }
        pricing_body = {
            "data": {
                "type": "flight-offers-pricing",
                "flightOffers": [selected_offer]
            }
        }

        pricing_response = requests.post(pricing_url, headers=pricing_headers, json=pricing_body)
        pricing_response.raise_for_status()
        confirmed_data = pricing_response.json()
        confirmed_offer = confirmed_data['data']['flightOffers'][0]
        confirmed_price = confirmed_offer['price']['total']
        print(f"💵 Confirmed price: {confirmed_price}")

        # ✈️ CREATE BOOKING (NEW SECTION)
        print("\n🧾 Creating test booking for first offer...")

        booking_url = f"{os.getenv('AMADEUS_BASE_URL')}/v1/booking/flight-orders"
        booking_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.amadeus+json"
        }

        traveler_info = [
            {
                "id": "1",
                "dateOfBirth": "1990-05-01",
                "name": {
                    "firstName": "Test",
                    "lastName": "User"
                },
                "gender": "MALE",
                "contact": {
                    "emailAddress": "test.user@example.com",
                    "phones": [
                        {
                            "deviceType": "MOBILE",
                            "countryCallingCode": "44",
                            "number": "7700000000"
                        }
                    ]
                },
                "documents": [
                    {
                        "documentType": "PASSPORT",
                        "birthPlace": "London",
                        "issuanceLocation": "London",
                        "issuanceDate": "2015-01-01",
                        "number": "123456789",
                        "expiryDate": "2030-01-01",
                        "issuanceCountry": "GB",
                        "validityCountry": "GB",
                        "nationality": "GB",
                        "holder": True
                    }
                ]
            }
        ]

        booking_body = {
            "data": {
                "type": "flight-order",
                "flightOffers": [confirmed_offer],
                "travelers": traveler_info,
                "remarks": {
                    "general": [
                        {
                            "subType": "GENERAL_MISCELLANEOUS",
                            "text": "Test booking"
                        }
                    ]
                },
                "ticketingAgreement": {
                    "option": "DELAY_TO_CANCEL",
                    "delay": "6D"
                },
                "contacts": [
                    {
                        "addresseeName": {
                            "firstName": "Support",
                            "lastName": "Team"
                        },
                        "companyName": "My Travel Co",
                        "purpose": "STANDARD",
                        "phones": [
                            {
                                "deviceType": "LANDLINE",
                                "countryCallingCode": "44",
                                "number": "1234567890"
                            }
                        ],
                        "emailAddress": "support@example.com",
                        "address": {
                            "lines": [
                                "123 Main Street"
                            ],
                            "postalCode": "W1A1AA",
                            "cityName": "London",
                            "countryCode": "GB"
                        }
                    }
                ]
            }
        }

        booking_response = requests.post(booking_url, headers=booking_headers, json=booking_body)

        if booking_response.status_code == 201:
            booking_data = booking_response.json()
            booking_id = booking_data['data']['id']
            print(f"✅ Booking created successfully! Booking ID: {booking_id}")
        else:
            print(f"❌ Booking failed with status {booking_response.status_code}")
            print(booking_response.text)

if __name__ == "__main__":
    test_flight_search_and_pricing()
    print('Done')