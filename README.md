# AI Flight Booking Assistant

This project is an intelligent flight booking assistant that integrates natural language understanding via OpenAI with real-time flight search through the Booking.com Flights API. It allows users to enter natural language prompts (e.g., "Find me a cheap return flight from London to Tokyo in July") and receive structured flight data in response.

## Features

- **Natural language processing** using OpenAI's Chat API
- **Real-time flight data** via the Booking.com Flights API (through RapidAPI)
- **Clean utility functions** to handle model prompts and API queries
- **Modular architecture** for easy extension and eventual integration with FastAPI

## Project Structure
```text
project/
│
├── utils/
│ ├── extract_flights.py # Functions to query the Booking.com API
│ └── openai_prompt.py # Helper to construct and send prompts to OpenAI
│
├── main.py # Entry point for the agent (to be implemented)
│
├── .env # Stores API keys and environment variables
├── config.ini # Configuration for API models and settings
└── README.md # Project overview and documentation
```

## Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/flight-booking-agent.git
   cd flight-booking-agent