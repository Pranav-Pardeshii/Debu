import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.providers.gemini_provider import LLMProviderException

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_title(topic: str) -> str:
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
        raise LLMProviderException(f"[TitleGenerationError]:{e}") from e

