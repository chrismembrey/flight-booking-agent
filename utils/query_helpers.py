def prepare_amadeus_query(query: dict) -> dict:
    """
    Clean and prepare a structured OpenAI-generated flight query 
    for use with the Amadeus API.

    Converts:
    - Boolean values (like True/False) to 'true'/'false' strings
    - Removes any None values
    - Ensures all values are valid Amadeus query params
    """
    cleaned = {}

    for k, v in query.items():
        if v is None:
            continue  # Skip None values
        if isinstance(v, bool):
            cleaned[k] = str(v).lower()  # Convert True → 'true'
        else:
            cleaned[k] = v

    return cleaned