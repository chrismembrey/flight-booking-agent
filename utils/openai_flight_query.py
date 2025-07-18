import os
import json
import configparser
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from config.prompts import SYSTEM_PROMPT, FLIGHT_JSON_SCHEMA

# Load secrets and config
load_dotenv(find_dotenv())

config = configparser.ConfigParser()
config.read("config.ini")
model = config["api"]["OPENAI_MODEL"]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_flight_query(user_text: str) -> dict:
    """
    Sends user input to OpenAI and extracts a structured flight query using function calling.

    Parameters:
        user_text (str): Natural language input describing a flight

    Returns:
        dict: Structured flight query matching the Booking.com schema

    Raises:
        ValueError: If OpenAI fails to return a valid tool call
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_flight_query",
                    "description": "Extract flight search parameters",
                    "parameters": FLIGHT_JSON_SCHEMA
                }
            }
        ],
        tool_choice={"type": "function", "function": {"name": "get_flight_query"}}
    )

    # Defensive handling in case OpenAI doesn't call the tool
    try:
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            raise ValueError("No tool call returned by OpenAI. Try rephrasing the input.")
        arguments = tool_calls[0].function.arguments
        return json.loads(arguments)
    except (AttributeError, IndexError, TypeError, json.JSONDecodeError) as e:
        raise ValueError("OpenAI returned an unexpected format. Try rephrasing the input.") from e
    

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