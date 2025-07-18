from utils.extract_flights import fetch_and_extract
from utils.openai_flight_query import get_flight_query
from utils.query_helpers import prepare_amadeus_query
from utils.chat_session import ChatSession

# Start conversation session
chat = ChatSession()

# Get user input and send to OpenAI to generate query
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
    "Example: London to Bordeaux, 1 adult, no children, direct, economy, 2025-10-15 to 2025-10-20, GBP\n> "
)

query = get_flight_query(user_input)
amadeus_cleaned_query = prepare_amadeus_query(query)
df = fetch_and_extract(amadeus_cleaned_query)

# Store full Amadeus offer objects by ID
raw_offers_by_id = {row["id"]: row["raw_offer"] for _, row in df.iterrows()}

# Add initial context to chat session
chat.add_user_message(user_input)

if df.empty:
    # Graceful handling if no offers were found
    chat.add_user_message("I'm sorry, we couldn't find any flights matching your search criteria at this time.")
    print("I'm sorry, we couldn't find any flights matching your search criteria at this time.")
else:
    print(f'{len(df)} Flights Returned!')
    chat.add_user_message("Here are the flight results:")
    # Convert DataFrame to string without raw_offer column becuase its so verbose 
    # and most key information i in the other fields 
    chat.add_user_message(df.drop(columns=["raw_offer"]).to_string(index=False))

# Enter into continuous dialogue
while True:
    follow_up = input("\nAsk a follow-up or type 'exit' to quit:\n> ")
    if follow_up.lower() == 'exit':
        break

    chat.add_user_message(follow_up)
    reply = chat.get_response()
    print(f"\nAssistant: {reply}")