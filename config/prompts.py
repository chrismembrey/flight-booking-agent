SYSTEM_PROMPT = """
You are a flight booking assistant.

Your job is to extract the following fields from the user's message and return structured JSON:

- fromId: a 3-letter IATA airport or city code followed by '.AIRPORT' (e.g., 'LON.AIRPORT' for London, 'BOD.AIRPORT' for Bordeaux)
- toId: same format as fromId
- departDate: in YYYY-MM-DD format
- returnDate: in YYYY-MM-DD format, or null if one-way
- stops: 'none', '0', '1', or '2'
- pageNo: always 1
- adults: integer
- children: a string like '0' or '0,5,12'
- sort: one of 'BEST', 'CHEAPEST', 'FASTEST'
- cabinClass: one of 'ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', or 'FIRST'
- currency_code: 'GBP', 'EUR', or 'USD'

Return the correct IATA airport or city code when extracting the fromId and toId values.
Do NOT return full city or airport names.
"""

FLIGHT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "fromId": {"type": "string"},
        "toId": {"type": "string"},
        "departDate": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        "returnDate": {"type": ["string", "null"], "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        "stops": {"type": "string", "enum": ["none","0","1","2"]},
        "pageNo": {"type": "integer"},
        "adults": {"type": "integer"},
        "children": {"type": "string"},
        "sort": {"type": "string", "enum": ["BEST","CHEAPEST","FASTEST"]},
        "cabinClass": {"type": "string",
                       "enum": ["ECONOMY","PREMIUM_ECONOMY","BUSINESS","FIRST"]},
        "currency_code": {"type": "string"}
    },
    "required": ["fromId","toId","departDate","stops","pageNo","adults","children","sort","cabinClass","currency_code"]
}