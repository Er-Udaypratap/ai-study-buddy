import os
from google import genai
from google.genai import types
from services.prompts import get_system_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Free-tier model (2026) - gemini-2.0-flash free tier band bandy; 2.5 series abhi free tier me hai
MODEL_NAME = "gemini-2.5-flash"


def get_ai_response(mode: str, user_message: str, chat_history: list, context: str = ""):
    system_prompt = get_system_prompt(mode, context)

    # Frontend se aata hai: [{"role": "user"/"model", "parts": ["text"]}]
    # Naye SDK ko chahiye: [{"role": "...", "parts": [{"text": "..."}]}]
    formatted_history = []
    for msg in chat_history:
        parts = [{"text": p} if isinstance(p, str) else p for p in msg.get("parts", [])]
        formatted_history.append({"role": msg["role"], "parts": parts})

    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=500,  # response chhota rakho - free quota bachane ke liye
            temperature=0.7,
        ),
        history=formatted_history,
    )

    response = chat.send_message(user_message)
    return response.text
