import os
import google.generativeai as genai
from services.prompts import get_system_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Free-tier friendly model - check ai.google.dev for the current free-tier model name/limits
MODEL_NAME = "gemini-2.0-flash"


def get_ai_response(mode: str, user_message: str, chat_history: list, context: str = ""):
    system_prompt = get_system_prompt(mode, context)

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
    )

    # chat_history format: [{"role": "user"/"model", "parts": ["text"]}]
    chat = model.start_chat(history=chat_history)

    response = chat.send_message(
        user_message,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=500,  # response chhota rakho - free quota bachane ke liye
            temperature=0.7,
        ),
    )

    return response.text
