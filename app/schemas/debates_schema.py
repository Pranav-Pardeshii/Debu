from pydantic import BaseModel
from enum import Enum

class GeminiModel(str, Enum):
    FLASH = "gemini-2.5-flash"

class CreateDebateRequest(BaseModel):
    topic: str
    proposition_model: GeminiModel = GeminiModel.FLASH
    opposition_model: GeminiModel = GeminiModel.FLASH
    max_turns: int = 6

class DebateResponse(BaseModel):
    debate_id: int
    title: str
    proposition_model: str
    opposition_model: str
    debate_state: str
    max_turns: int
    
    model_config= {
        'from_attributes':True
    }