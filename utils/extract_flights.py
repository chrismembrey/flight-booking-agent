import os
import requests
import pandas as pd
import configparser
from dotenv import load_dotenv, find_dotenv

# Load .env and config
load_dotenv(find_dotenv())
config = configparser.ConfigParser()
config.read('config.ini')
URL = config['api']['RAPID_API_BOOKING_PATH']

HEADERS = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

def extract_flights_from_response(raw_json: dict) -> pd.DataFrame:
    """Parse raw API response JSON into a structured Pandas DataFrame."""
    flights = raw_json.get('data', {})
    offers = flights.get('flightOffers', [])

    flight_rows = []
    for offer in offers:
        token = offer.get('token', '')
        price = offer.get('priceBreakdown', {}).get('total', {})
        total_price = price.get('units', 0) + price.get('nanos', 0) / 1e9

        for segment in offer.get('segments', []):
            for leg in segment.get('legs', []):
                flight_rows.append({
                    'token': token,
                    'departure_airport': leg.get('departureAirport', {}).get('code', ''),
                    'arrival_airport': leg.get('arrivalAirport', {}).get('code', ''),
                    'departure_time': leg.get('departureTime', ''),
                    'arrival_time': leg.get('arrivalTime', ''),
                    'carrier': ', '.join(c.get('name', '') for c in leg.get('carriersData', [])),
                    'flight_number': leg.get('flightInfo', {}).get('flightNumber', ''),
                    'cabin_class': leg.get('cabinClass', 'ECONOMY'),
                    'total_price': total_price
                })

    df = pd.DataFrame(flight_rows)
    if df.empty:
        return df

    df['departure_time'] = pd.to_datetime(df['departure_time'])
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])

    # Sort legs by departure time within each token
    df = df.sort_values(['token', 'departure_time'])

    # Classify direction: first leg = outbound, rest = inbound (simplified fallback)
    df['direction'] = df.groupby('token')['departure_time'] \
                        .rank(method='first', ascending=True) \
                        .apply(lambda x: 'outbound' if x == 1 else 'inbound')

    # Build route strings per token+direction
    df['leg_route'] = df['departure_airport'] + ' > ' + df['arrival_airport']
    routes = df.groupby(['token', 'direction'])['leg_route'].apply(lambda x: ' > '.join(x)).reset_index(name='route')

    # Collapse relevant fields per token+direction
    summary = df.groupby(['token', 'direction']).agg({
        'departure_time': 'first',
        'arrival_time': 'last',
        'carrier': lambda x: ', '.join(set(x.dropna())),
        'flight_number': 'first',
        'cabin_class': 'first',
        'total_price': 'first'
    }).reset_index()

    # Merge in route strings
    summary = summary.merge(routes, on=['token', 'direction'], how='left')

    # Pivot to wide format (one row per token)
    df = summary.pivot_table(index='token', columns='direction', aggfunc='first')
    df.columns = ['_'.join(col) for col in df.columns]
    df.reset_index(inplace=True)

    # Ensure columns exist
    outbound = [
        'route_outbound', 'departure_time_outbound', 'arrival_time_outbound',
        'carrier_outbound', 'flight_number_outbound', 'cabin_class_outbound',
        'total_price_outbound'
    ]
    inbound = [
        'route_inbound', 'departure_time_inbound', 'arrival_time_inbound',
        'carrier_inbound', 'flight_number_inbound', 'cabin_class_inbound',
        'total_price_inbound'
    ]
    for col in outbound + inbound:
        df[col] = df.get(col)

    # Rearrange and clean columns
    df = df[['token'] + outbound + inbound]
    df.rename(columns={'total_price_outbound': 'total_price'}, inplace=True)
    df.drop(columns=['total_price_inbound'], inplace=True, errors='ignore')

    df['trip_type'] = df['route_inbound'].apply(
        lambda x: 'one-way' if pd.isna(x) else 'return'
    )

    cols = [c for c in df.columns if c != 'total_price'] + ['total_price']
    return df[cols]


def fetch_and_extract(query: dict) -> pd.DataFrame:
    """
    Combine API call and extraction.
    `query` should be the JSON from OpenAI containing flight search parameters.
    """
    response = requests.get(URL, headers=HEADERS, params=query)
    data = response.json()
    return extract_flights_from_response(data)