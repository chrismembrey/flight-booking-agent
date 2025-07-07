from utils.extract_flights import fetch_and_extract
from utils.openai_flight_query import get_flight_query
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
    "Example: London to Bordeaux, 1 adult, no children, direct, economy, 2025-07-15 to 2025-07-20, GBP\n> "
)

query = get_flight_query(user_input)
df = fetch_and_extract(query)

# Add initial context to chat session
chat.add_user_message(user_input)
chat.add_user_message("Here are the flight results:")
chat.add_user_message(df.to_string(index=False))

# Enter into continuous dialogue
while True:
    follow_up = input("\nAsk a follow-up or type 'exit' to quit:\n> ")
    if follow_up.lower() == 'exit':
        break

    chat.add_user_message(follow_up)
    reply = chat.get_response()
    print(f"\nAssistant: {reply}")