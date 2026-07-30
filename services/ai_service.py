import os
from google import genai
from google.genai import types
from services.prompts import get_system_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Confirmed available models (from /api/models check) - "latest" alias future-proof hai
MODEL_CANDIDATES = ["gemini-flash-lite-latest", "gemini-2.5-flash-lite", "gemini-2.5-flash"]


def get_ai_response(mode: str, user_message: str, chat_history: list, context: str = ""):
    system_prompt = get_system_prompt(mode, context)

    # Frontend se aata hai: [{"role": "user"/"model", "parts": ["text"]}]
    # Naye SDK ko chahiye: [{"role": "...", "parts": [{"text": "..."}]}]
    formatted_history = []
    for msg in chat_history:
        parts = [{"text": p} if isinstance(p, str) else p for p in msg.get("parts", [])]
        formatted_history.append({"role": msg["role"], "parts": parts})

    errors = []
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
            errors.append(f"{model_name}: {str(e)}")
            continue  # agla model try karo

    # Sabhi models fail ho gaye
    raise Exception(" | ".join(errors))
