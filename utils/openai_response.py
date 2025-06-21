from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv
import configparser

env = load_dotenv(find_dotenv())

config = configparser.ConfigParser()
config.read('config.ini')
openai_model = config['api']['OPENAI_MODEL']

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

completion = client.chat.completions.create(
  model=openai_model,
  store=False,
  messages=[
    {"role": "user", "content": "write a story about a girl called lola who lives on a farm and makes a spag bol she calls slag bol. In the short story ensure she comes across as a complete slag."}
  ]
)

print(completion.choices[0].message);