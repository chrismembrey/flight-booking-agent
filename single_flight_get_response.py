import requests
from utils.extract_flights import extract_flights_from_response

url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"

querystring = {'fromId': 'LON.AIRPORT', 'toId': 'BOD.AIRPORT', 'departDate': '2025-07-15', 'returnDate': '2025-07-20',
               'stops': '0', 'pageNo': 1, 'adults': 1, 
               'children': '0', 'sort': 'BEST', 'cabinClass': 'ECONOMY', 'currency_code': 'GBP'}

headers = {
	"x-rapidapi-key": "2bf531d232msh356243daf3fa35ap1f9288jsn3c1125b0712f",
	"x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

extracted_flights = extract_flights_from_response(response.json())

extracted_flights.to_csv('extracted_flight_test.csv', index = False)