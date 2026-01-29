import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API Key found in .env")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Listing available models...")
    # The SDK might differ slightly, let's try standard listing
    # google-genai v1.0+ uses client.models.list()
    for m in client.models.list():
        if "gemini" in m.name:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
