# utils/chat_session.py
from typing import List, Dict, Any
from openai import OpenAI
import configparser
import os
from dotenv import load_dotenv, find_dotenv

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