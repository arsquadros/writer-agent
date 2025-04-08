from typing import List
from dotenv import load_dotenv

import os

import openai

load_dotenv()

def get_text_response(env_path: str, messages: List[dict],
                      model: str = "gpt-4o-mini", temperature: float = 0.5, n: int = 1) -> str:
    """
    Get Text Response from OpenAI's ChatGPT response.

    Raises errors if any parameter is invalid.
    """

    openai.api_key = os.getenv(env_path, "")
    result = openai.chat.completions.create(model=model, messages=messages, temperature=temperature, n=n)
    return result.choices[0].message.content
