import os
import requests
import pandas as pd
from utils.amadeus_auth import get_amadeus_access_token
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())


def query_amadeus_flight_offers(query: dict) -> list:
    """
    Send a GET request to the Amadeus Flight Offers Search API using the given query parameters.

    Args:
        query (dict): Dictionary of query parameters, including IATA codes, dates, etc.

    Returns:
        list: A list of raw flight offer objects returned by the Amadeus API.
    """
    url = f"{os.getenv('AMADEUS_BASE_URL')}/v2/shopping/flight-offers"
    token = get_amadeus_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send the request to Amadeus API
    response = requests.get(url, headers=headers, params=query)
    response.raise_for_status()  # Raise error if request fails
    return response.json().get("data", [])  # Return list of flight offers


def extract_flight_offer_summary(offer: dict) -> dict:
    """
    Flatten a single flight offer into a summary dictionary with human-readable fields.

    Args:
        offer (dict): One raw flight offer object from Amadeus.

    Returns:
        dict: A flattened summary of the flight offer including route, price, and carriers.
    """
    itineraries = offer.get("itineraries", [])
    total_price = offer.get("price", {}).get("total", "N/A")
    currency = offer.get("price", {}).get("currency", "EUR")

    # Extract outbound and inbound segment groups
    outbound = itineraries[0]["segments"]
    inbound = itineraries[1]["segments"] if len(itineraries) > 1 else []

    def segment_summary(segments):
        """
        Summarises a list of segments into route, departure/arrival times, and carrier info.
        """
        if not segments:
            return "", "", "", ""

        dep = segments[0]["departure"]
        arr = segments[-1]["arrival"]

        # Format: A > B > C
        route = " > ".join([seg["departure"]["iataCode"] for seg in segments] + [arr["iataCode"]])

        # Carriers involved
        carrier = ", ".join(set(seg["carrierCode"] for seg in segments))

        # Full flight numbers
        flight_nums = ", ".join([f'{seg["carrierCode"]}{seg["number"]}' for seg in segments])

        return route, dep["at"], arr["at"], f"{carrier} ({flight_nums})"

    # Extract summaries
    outbound_route, dep_out, arr_out, carrier_out = segment_summary(outbound)
    inbound_route, dep_in, arr_in, carrier_in = segment_summary(inbound)

    return {
        "id": offer.get("id"),
        "price": float(total_price),
        "currency": currency,
        "outbound_route": outbound_route,
        "outbound_departure": dep_out,
        "outbound_arrival": arr_out,
        "outbound_carrier": carrier_out,
        "inbound_route": inbound_route,
        "inbound_departure": dep_in,
        "inbound_arrival": arr_in,
        "inbound_carrier": carrier_in,
        "trip_type": "return" if inbound_route else "one-way",
        "raw_offer": offer  # Full offer object for pricing and booking later
    }


def extract_flights_from_response(offers: list) -> pd.DataFrame:
    """
    Convert a list of Amadeus flight offers into a pandas DataFrame of flattened rows.

    Args:
        offers (list): A list of raw offer objects from Amadeus.

    Returns:
        pd.DataFrame: DataFrame containing clean, structured flight info + raw offer.
    """
    rows = [extract_flight_offer_summary(offer) for offer in offers]
    return pd.DataFrame(rows)


def fetch_and_extract(query: dict) -> pd.DataFrame:
    """
    Full wrapper: fetch flight offers from Amadeus and convert them into a summary DataFrame.

    Args:
        query (dict): Dictionary of search parameters formatted for Amadeus API.

    Returns:
        pd.DataFrame: Structured DataFrame of available flight offers.
    """
    offers = query_amadeus_flight_offers(query)
    
    # If no offers were found, return an empty DataFrame with the correct columns
    if not offers:
        return pd.DataFrame(columns=[
            "id", "price", "currency", 
            "outbound_route", "outbound_departure", "outbound_arrival", "outbound_carrier", 
            "inbound_route", "inbound_departure", "inbound_arrival", "inbound_carrier", 
            "trip_type", "raw_offer"
        ])
    
    return extract_flights_from_response(offers)