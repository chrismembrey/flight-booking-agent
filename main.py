from utils.extract_flights import fetch_and_extract
from utils.openai_flight_query import get_flight_query

#---

# import requests
# import os
# import requests
# import pandas as pd
# import configparser
# from dotenv import load_dotenv, find_dotenv

# # Load .env and config
# load_dotenv(find_dotenv())
# config = configparser.ConfigParser()
# config.read('config.ini')
# URL = config['api']['RAPID_API_BOOKING_PATH']

# HEADERS = {
#     "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
#     "x-rapidapi-host": "booking-com15.p.rapidapi.com"
# }

#--- 


user_input = input(
    "Enter your flight search including:\n"
    "- Departure city or airport\n"
    "- Destination city or airport\n"
    "- Departure date (YYYY-MM-DD)\n"
    "- Optional return date (YYYY-MM-DD)\n"
    "- Number of adults\n"
    "- Children ages (comma‑separated), or none\n"
    "- Stops preference (none, 0, 1, 2)\n"
    "- Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)\n"
    "- Currency (GBP, EUR, USD)\n"
    "Example: London to Bordeaux, 1 adult, no children, direct, economy, 2025-07-15 to 2025-07-20, GBP\n> "
)

query = get_flight_query(user_input)
df = fetch_and_extract(query)
print('DataFrame:')
print(df.head())