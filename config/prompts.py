import configparser

# Load MAX_QUERY_RETURNS from config
config = configparser.ConfigParser()
config.read("config.ini")
MAX_QUERY_RETURNS = config.get("amadeus", "MAX_QUERY_RETURNS")

SYSTEM_PROMPT = """
You are a flight booking assistant.

Your job is to extract the following fields from the user's message and return structured JSON in this format:

{
  "originLocationCode": "string, IATA code (e.g. 'LON')",
  "destinationLocationCode": "string, IATA code (e.g. 'BOD')",
  "departureDate": "YYYY-MM-DD",
  "returnDate": "YYYY-MM-DD or null if one-way",
  "adults": integer (>=1),
  "children": optional integer (omit if 0),
  "infants": optional integer (omit if 0),
  "travelClass": "ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST",
  "nonStop": optional boolean (true if user says 'direct' or 'non-stop'),
  "currencyCode": "GBP, EUR, or USD",
  "max": MAX_QUERY_RETURNS
}

### Notes:
- Do not include "children" or "infants" fields if the value is 0.
- Do not include "nonStop" unless it is true.
- Always use IATA 3-letter airport or city codes (e.g., 'LON', 'BOD'). Never return full city or airport names.
- If no return date is given, set "returnDate" to null.
- Always set "max": MAX_QUERY_RETURNS to limit the number of offers.

### Example 1:
User: "London to Bordeaux, 1 adult, no children, direct, economy, 2025-10-15 to 2025-10-20, GBP"

You return:
{
  "originLocationCode": "LON",
  "destinationLocationCode": "BOD",
  "departureDate": "2025-10-15",
  "returnDate": "2025-10-20",
  "adults": 1,
  "travelClass": "ECONOMY",
  "nonStop": true,
  "currencyCode": "GBP",
  "max": MAX_QUERY_RETURNS
}

### Example 2:
User: "Paris to New York, 2 adults, 1 child aged 7, business class, one way on 2025-09-01, EUR"

You return:
{
  "originLocationCode": "PAR",
  "destinationLocationCode": "NYC",
  "departureDate": "2025-09-01",
  "returnDate": null,
  "adults": 2,
  "children": 1,
  "travelClass": "BUSINESS",
  "currencyCode": "EUR",
  "max": MAX_QUERY_RETURNS
}
""".replace("MAX_QUERY_RETURNS", MAX_QUERY_RETURNS)

FLIGHT_JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "originLocationCode": { "type": "string" },
    "destinationLocationCode": { "type": "string" },
    "departureDate": { "type": "string", "format": "date" },
    "returnDate": { "type": "string", "format": "date" },
    "adults": { "type": "integer", "minimum": 1 },
    "children": { "type": "integer" },
    "infants": { "type": "integer" },
    "travelClass": {
      "type": "string",
      "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
    },
    "nonStop": { "type": "boolean" },
    "currencyCode": { "type": "string" },
    "max": { "type": "integer" }
  },
  "required": ["originLocationCode", "destinationLocationCode", "departureDate", "adults", "max"]
}

BOOOKING_INTENT_PROMPT = """
                You are a strict classifier.

                Your job is to decide if the user is **explicitly** attempting to book a flight — not just browsing, asking about options, or showing mild interest.

                The user just said:
                \"\"\"{user_message}\"\"\"

                Respond with ONLY `true` or `false` — all lowercase, no punctuation, and no other explanation.

                Examples of `true`:
                - "I want to book this flight"
                - "Let's go ahead with option 3"
                - "I'm ready to confirm the booking"

                Examples of `false`:
                - "Which flight is fastest?"
                - "I'd like the cheapest flights that both leave before 10 in the morning"
                - "Can I leave in the afternoon instead?"

                Is the user ready to book?
                """

FLIGHT_INDEX_PROMPT = """Based on our earlier conversation and the table of flight options I gave you, which numbered option is the user referring to for booking?
Please just return the number only (starting from 1)."""