import os
from google import genai
from google.genai import types
from services.prompts import get_system_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Free-tier models (2026) - list me order matters, pehla try hoga, fail hone par agla
MODEL_CANDIDATES = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-flash-lite"]


def get_ai_response(mode: str, user_message: str, chat_history: list, context: str = ""):
    system_prompt = get_system_prompt(mode, context)

    # Frontend se aata hai: [{"role": "user"/"model", "parts": ["text"]}]
    # Naye SDK ko chahiye: [{"role": "...", "parts": [{"text": "..."}]}]
    formatted_history = []
    for msg in chat_history:
        parts = [{"text": p} if isinstance(p, str) else p for p in msg.get("parts", [])]
        formatted_history.append({"role": msg["role"], "parts": parts})

    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=500,  # response chhota rakho - free quota bachane ke liye
                    temperature=0.7,
                ),
                history=formatted_history,
            )
            response = chat.send_message(user_message)
            return response.text
        except Exception as e:
            last_error = e
            continue  # agla model try karo

    # Sabhi models fail ho gaye
    raise last_error
