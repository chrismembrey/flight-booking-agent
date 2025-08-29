# utils/chat_session.py
from typing import List, Dict, Any
from openai import OpenAI
import configparser
import os
from dotenv import load_dotenv, find_dotenv
from config.prompts import BOOOKING_INTENT_PROMPT, FLIGHT_INDEX_PROMPT
import json

json()

# Load environment variables and config
load_dotenv(find_dotenv())
config = configparser.ConfigParser()
config.read("config.ini")

# Set up OpenAI client and model
openai_model = config["api"]["OPENAI_MODEL"]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatSession:
    def __init__(self, system_prompt: str = "You are a helpful flight assistant."):
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt, "display": False}
        ]

    def add_user_message(self, content: str, display: bool = True):
        self.messages.append({"role": "user", "content": content, "display": display})

    def add_assistant_message(self, content: str, display: bool = True):
        self.messages.append({"role": "assistant", "content": content, "display": display})

    def get_response(self) -> str:
        try:
            # Remove 'display' key before sending to OpenAI
            cleaned_messages = [
                {k: v for k, v in m.items() if k in {"role", "content"}}
                for m in self.messages
            ]
            completion = client.chat.completions.create(
                model=openai_model,
                messages=cleaned_messages,
                store=False
            )
            response_content = completion.choices[0].message.content
            self.add_assistant_message(response_content)
            return response_content
        except Exception as e:
            raise RuntimeError(f"Failed to get OpenAI response: {e}")

    def get_display_messages(self) -> List[Dict[str, str]]:
        return [m for m in self.messages if m.get("display", True)]

    def detect_booking_intent(self, user_message: str) -> bool:
        """
        Return True only if the user is explicitly ready to book a flight.
        Examples that should return True:
        - "I want to book now"
        - "Can we go ahead with this one?"
        - "I'm ready to confirm"

        Examples that should return False:
        - "Can you tell me more about this flight?"
        - "Is baggage included?"
        - "I might book soon"

        Returns:
            bool: whether the user shows booking intent
        """
        prompt = BOOOKING_INTENT_PROMPT.format(user_message=user_message)

        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.choices[0].message.content.strip().lower()
            return content == "true"
        except Exception as e:
            raise RuntimeError(f"Failed to detect booking intent: {e}")
        
    def identify_flight_index(self) -> int | None:
        """
        Ask the LLM to infer which flight option (index) the user is referring to based on prior chat history.
        Returns an integer index if one is found, else None.
        """
        cleaned_messages = [
            {k: v for k, v in m.items() if k in {"role", "content"}}
            for m in self.messages
        ]
        cleaned_messages.append({
            "role": "user",
            "content": FLIGHT_INDEX_PROMPT
        })

        try:
            completion = client.chat.completions.create(
                model=openai_model,
                messages=cleaned_messages,
                store=False
            )
            response_text = completion.choices[0].message.content.strip()
            if response_text.isdigit():
                return int(response_text) - 1  # to match DataFrame indexing
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to identify flight index: {e}")