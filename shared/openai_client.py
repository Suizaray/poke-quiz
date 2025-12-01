import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Loads .env into the process environment

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None