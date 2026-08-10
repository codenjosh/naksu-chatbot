import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from langfuse import get_client
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

import requests

# Loads the local .env file in development. Render supplies the same variables
# through its service Environment settings.
load_dotenv()

print("=== LANGFUSE CHECK ===")
print("Public key exists:", bool(os.getenv("LANGFUSE_PUBLIC_KEY")))
print("Secret key exists:", bool(os.getenv("LANGFUSE_SECRET_KEY")))
print("Base URL:", os.getenv("LANGFUSE_BASE_URL"))
print("======================")

# Initialize Langfuse
langfuse = get_client()

# Instrument Google Gemini
GoogleGenAIInstrumentor().instrument()

# -------------------------
# Gemini configuration
# -------------------------

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")

gemini_client = genai.Client(api_key=api_key)


def ask_gemini(messages):
    """Send conversation history to Google Gemini."""

    contents = []

    for message in messages:
        role = "model" if message["role"] == "assistant" else "user"

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part(text=message["content"])
                ]
            )
        )

    response = gemini_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents
    )

    return response.text


# -------------------------
# Local Llama configuration
# -------------------------

def ask_llama(messages):
    response = requests.post(
        "http://ollama:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": messages,
            "stream": False
        }
    )

    return response.json()["message"]["content"]
