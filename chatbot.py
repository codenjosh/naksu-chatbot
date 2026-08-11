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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")


class ChatbotError(RuntimeError):
    """A safe, user-facing error raised by a model provider."""


def _gemini_error_message(error):
    error_text = str(error)
    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
        return (
            "Gemini's request quota has been reached. Wait for the quota to reset, "
            "or increase the Gemini API quota, then try again."
        )
    if "401" in error_text or "403" in error_text:
        return "Gemini rejected the API key. Check GOOGLE_API_KEY in your deployment settings."
    return "Gemini could not complete that request. Please try again in a moment."


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

    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        )
    except Exception as error:
        raise ChatbotError(_gemini_error_message(error)) from error

    if not response.text:
        raise ChatbotError("Gemini returned an empty response. Please try again.")

    return response.text


# -------------------------
# Local Llama configuration
# -------------------------

def ask_llama(messages):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": "llama3.2",
                "messages": messages,
                "stream": False,
            },
            timeout=(5, 120),
        )
        response.raise_for_status()
        content = response.json().get("message", {}).get("content")
    except requests.ConnectionError as error:
        raise ChatbotError(
            "Llama is not reachable. On Render, deploy an Ollama service and set "
            "OLLAMA_URL, or switch to Gemini API."
        ) from error
    except requests.Timeout as error:
        raise ChatbotError("Llama took too long to respond. Please try again.") from error
    except requests.RequestException as error:
        raise ChatbotError("Llama returned an error. Check the Ollama service logs.") from error
    except ValueError as error:
        raise ChatbotError("Llama returned an invalid response. Please try again.") from error

    if not content:
        raise ChatbotError("Llama returned an empty response. Please try again.")

    return content
