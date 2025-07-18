import streamlit as st
from utils.openai_flight_query import get_flight_query
from utils.query_helpers import prepare_amadeus_query
from utils.extract_flights import fetch_and_extract
from utils.chat_session import ChatSession

st.set_page_config(page_title="AI Flight Booking Assistant", layout="centered")

st.title("✈️ AI Flight Booking Assistant")

# Initialise session state
if "chat" not in st.session_state:
    st.session_state.chat = ChatSession()
if "df" not in st.session_state:
    st.session_state.df = None

with st.form("flight_form"):
    user_input = st.text_area(
        "Enter your flight search:",
        placeholder="e.g. London to Bordeaux, 1 adult, no children, direct, economy, 2025-07-15 to 2025-07-20, GBP",
        height=150
    )
    submitted = st.form_submit_button("Search Flights")

if submitted and user_input:
    try:
        with st.spinner("Retrieving Flight Data..."):
            query = get_flight_query(user_input)
            amadeus_cleaned_query = prepare_amadeus_query(query)
            df = fetch_and_extract(amadeus_cleaned_query)

            if df.empty:
                st.session_state.df = None  # clear old results
                st.warning("Sorry, we couldn't find any flights matching your search. Try different dates or airports.")
            else:
                st.session_state.df = df.drop(columns=["raw_offer"])

            # Add context to chat
            st.session_state.chat.add_user_message(user_input)
            # Add flight results to internal memory, not shown in UI
            st.session_state.chat.add_user_message("Here are the flight results:", display=False)
            st.session_state.chat.add_user_message(df.to_string(index=False), display=False)

        st.success("Flights fetched successfully.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

# --- Always visible restart button ---
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 Start a New Search"):
        st.session_state.df = None
        st.session_state.chat = ChatSession()
        st.session_state.chat_round = 0
        st.experimental_rerun()

# --- Results section ---
if st.session_state.df is not None:
    st.subheader("Available Flights")
    st.dataframe(st.session_state.df)

    st.subheader("💬 Chat with your Assistant")

    for message in st.session_state.chat.get_display_messages():
        role = "You" if message["role"] == "user" else "Assistant"
        st.markdown(f"**{role}:** {message['content']}")

    if "chat_round" not in st.session_state:
        st.session_state.chat_round = 0

    follow_up = st.text_input(
        "Your follow-up question:",
        key=f"follow_up_input_{st.session_state.chat_round}",
        placeholder="Ask about flight details, prices, etc."
    )

    if st.button("Send"):
        if follow_up.strip():
            st.session_state.chat.add_user_message(follow_up)
            with st.spinner("Thinking..."):
                reply = st.session_state.chat.get_response()
            st.session_state.chat_round += 1
            st.rerun()
        else:
            st.warning("Please enter a message.")