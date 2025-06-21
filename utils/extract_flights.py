import requests
import numpy as np
import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import configparser

# Load environment variables from .env file
load_dotenv(find_dotenv())

config = configparser.ConfigParser()
config.read('config.ini')
url = config['api']['RAPID_API_BOOKING_PATH']

querystring = {
    "fromId": "LON.AIRPORT",         # London
    "toId": "BOD.AIRPORT",           # Bordeaux
    "departDate": "2025-08-15",      # Summer
    "returnDate": "2025-08-20",      # Summer return
    "stops": "0",                 # Direct flight
    "pageNo": "1",
    "adults": "1",                   # 1 adult
    "children": "0",                 # No children
    "sort": "BEST",
    "cabinClass": "ECONOMY",
    "currency_code": "GBP"           # Currency in GBP
}

# Load API key securely from .env
headers = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

# response = requests.get(url, headers=headers, params=querystring)
# print(response.json())

# Read the file as a raw text string
with open('tests/example_flight_response.txt', 'r') as file:
    raw_data = file.read()

# Extract the list of flight options
flights = eval(raw_data)['data']


# Extract flight offers
flight_offers = flights['flightOffers']

# Prepare a list to store extracted flight data
flight_data = []

# Extracting data from each flight offer
for offer in flight_offers:
    token = offer.get('token', '')
    price_info = offer.get('priceBreakdown', {})
    total_price = price_info.get('total', {}).get('units', 0) + price_info.get('total', {}).get('nanos', 0) / 1e9

    for segment in offer.get('segments', []):
        for leg in segment.get('legs', []):
            flight_data.append({
                'token': token,
                'departure_airport': leg.get('departureAirport', {}).get('code', ''),
                'arrival_airport': leg.get('arrivalAirport', {}).get('code', ''),
                'departure_time': leg.get('departureTime', ''),
                'arrival_time': leg.get('arrivalTime', ''),
                'carrier': ', '.join([carrier.get('name', '') for carrier in leg.get('carriersData', [])]),
                'flight_number': leg.get('flightInfo', {}).get('flightNumber', ''),
                'cabin_class': leg.get('cabinClass', 'ECONOMY'),
                'total_price': total_price
            })

# Convert the extracted data into a DataFrame
df = pd.DataFrame(flight_data)

# Convert departure_time to datetime for sorting
df['departure_time'] = pd.to_datetime(df['departure_time'])

# Count how many times each token appears
token_counts = df['token'].value_counts()

# Add direction based on time order per token
df['direction'] = df.groupby('token')['departure_time'].rank(method='first', ascending=True)
df['direction'] = df['direction'].apply(lambda x: 'outbound' if x == 1 else 'inbound')


# Pivot the dataframe
df = df.pivot(index='token', columns='direction')

# Flatten column names
df.columns = ['_'.join(col) for col in df.columns]
df.reset_index(inplace=True)

# Define desired column order: outbound first, then inbound
outbound_cols = [
    'departure_airport_outbound', 'arrival_airport_outbound', 'departure_time_outbound',
    'arrival_time_outbound', 'carrier_outbound', 'flight_number_outbound',
    'cabin_class_outbound', 'total_price_outbound'
]

inbound_cols = [
    'departure_airport_inbound', 'arrival_airport_inbound', 'departure_time_inbound',
    'arrival_time_inbound', 'carrier_inbound', 'flight_number_inbound',
    'cabin_class_inbound', 'total_price_inbound'
]

# Add any missing columns (for one-way flights)
for col in outbound_cols + inbound_cols:
    if col not in df.columns:
        df[col] = pd.NA

# Reorder the columns
df = df[['token'] + outbound_cols + inbound_cols]

# Remove duplicate total price column (from inbound)
df = df.drop(columns=['total_price_inbound'])

# Rename the outbound one to total_price
df = df.rename(columns={'total_price_outbound': 'total_price'})

# Add a trip_type column based on whether inbound departure airport is present
df['trip_type'] = df['departure_airport_inbound'].apply(
    lambda x: 'one-way' if pd.isna(x) else 'return'
)

# Move total_price to the end
cols = [col for col in df.columns if col != 'total_price'] + ['total_price']
df = df[cols]

# Display the DataFrame
df.to_csv('flight_data_test.csv', index=False)