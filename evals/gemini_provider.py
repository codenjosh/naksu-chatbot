"""Promptfoo provider that evaluates the same Gemini path as the chatbot."""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Promptfoo loads this file from its worker location, not from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# dotenv's default lookup starts from Promptfoo's worker directory, so load the
# project's development credentials explicitly before importing the chatbot.
load_dotenv(PROJECT_ROOT / ".env")

from chatbot import ask_gemini


def call_api(prompt, options, context):
    """Return a Promptfoo-compatible result for one chatbot prompt."""
    try:
        output = ask_gemini([{"role": "user", "content": str(prompt)}])
    except Exception as error:
        return {"error": f"Gemini request failed: {type(error).__name__}"}

    return {"output": output}
