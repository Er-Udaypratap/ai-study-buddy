import os
import base64
import time
from google import genai
from google.genai import types
from services.prompts import get_system_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Sirf "-latest" aliases use karo - ye Google ke rolling stable pointers hain,
# dated model names (2.5-flash, 2.5-flash-lite) baar baar deprecate ho rahe hain
MODEL_CANDIDATES = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-pro-latest"]


def _parse_data_url(data_url: str):
    """'data:image/jpeg;base64,....' se mime type aur raw bytes nikalta hai"""
    header, b64data = data_url.split(",", 1)
    mime_type = header.split(":")[1].split(";")[0]
    return mime_type, base64.b64decode(b64data)


def get_ai_response(
    mode: str,
    user_message: str,
    chat_history: list,
    context: str = "",
    image_data_url: str | None = None,
):
    system_prompt = get_system_prompt(mode, context)

    # Frontend se aata hai: [{"role": "user"/"model", "parts": ["text"]}]
    # Naye SDK ko chahiye: [{"role": "...", "parts": [{"text": "..."}]}]
    formatted_history = []
    for msg in chat_history:
        parts = [{"text": p} if isinstance(p, str) else p for p in msg.get("parts", [])]
        formatted_history.append({"role": msg["role"], "parts": parts})

    # Current message ke content parts banao - agar image hai toh usko bhi shamil karo
    message_parts = []
    if image_data_url:
        try:
            mime_type, image_bytes = _parse_data_url(image_data_url)
            message_parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        except Exception:
            pass  # image parse fail ho toh sirf text bhej do
    message_parts.append(user_message)

    errors = []
    for model_name in MODEL_CANDIDATES:
        # Temporary errors (503/UNAVAILABLE) ke liye 2 retry karo isi model pe
        for attempt in range(2):
            try:
                chat = client.chats.create(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=500,
                        temperature=0.7,
                    ),
                    history=formatted_history,
                )
                response = chat.send_message(message_parts)
                return response.text
            except Exception as e:
                err_str = str(e)
                errors.append(f"{model_name}: {err_str}")
                is_temporary = "503" in err_str or "UNAVAILABLE" in err_str
                if is_temporary and attempt == 0:
                    time.sleep(1.5)  # thoda wait karke isi model ko phir try karo
                    continue
                break  # permanent error (404 etc) - agla model try karo

    # Sabhi models fail ho gaye
    raise Exception(" | ".join(errors))
