import asyncio
import os
from typing import AsyncIterator
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


async def generate_title(topic: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = types.GenerateContentConfig(
        system_instruction="You are the model made for generating titles for debate topics, your one and only job is to create titles. Generate a maximum 5 words long title for the given topic. The title must be gramatically correct and logically sensible.",
        temperature=0.3,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    ),
    )
    try:
        response = await client.aio.models.generate_content(
            model = "gemini-2.5-flash",
            contents = topic,
            config=config,
        )
        return response.text
        
    except Exception as e:
        raise RuntimeError(f"[TitleGenerationError]:{e}") from e

if __name__ == '__main__':
    title = asyncio.run(generate_title("Racism good or bad"))
    print(title)