import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()


# --- Custom Exception class ---
class LLMProviderException(Exception):
    pass 

# Convert ORM to Python object
@dataclass
class ConversationTurn:
    role: str
    content: str

class LLMProvider(ABC):
    # Every child class should have this function
    @abstractmethod
    async def generate_response(self, history: list[ConversationTurn], current_speaker: str, system_instruction: str) -> AsyncIterator:
        """Yield response chunks as the stream in"""

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) # Instead of creating client everytime, we initialize it once per object

    async def generate_response(self, history: list[ConversationTurn], current_speaker: str, system_instruction: str) -> AsyncIterator:
        contents = []
        # Convert history to standerd genai sdk form
        for msg in history:
            role = "model" if msg.role == current_speaker else "user"
            contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
            )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.5,
        )   

        try:
            response = await self.client.aio.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents,
                config= config
            )   

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except errors.ClientError as e:
            raise LLMProviderException(f"\nClient Error: {e}") from e
        
        except Exception as e:
            raise LLMProviderException(f"\n[UNEXPECTED ERROR] {type(e).__name__}: {e}") from e

