import os
import configparser
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

# Load environment variables from .env
load_dotenv(find_dotenv())

# Read OpenAI model from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
openai_model = config['api']['OPENAI_MODEL']

# Initialize OpenAI client using the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def return_openai_output(prompt: str) -> str:
    """
    Generate a response from the OpenAI chat model using a given prompt.

    Parameters:
        prompt (str): The user message to send to the model.

    Returns:
        str: The content of the model's response.
    """
    try:
        completion = client.chat.completions.create(
            model=openai_model,
            store=False,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract the content from the first message choice
        message: ChatCompletionMessage = completion.choices[0].message
        return message.content

    except Exception as e:
        raise RuntimeError(f"Failed to get OpenAI response: {e}")