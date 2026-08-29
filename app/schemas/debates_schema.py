from pydantic import BaseModel


class CreateDebateRequest(BaseModel):
    topic: str
    proposition_model: str = 'gemini-2.5-flash'
    opposition_model: str = 'gemini-2.5-flash'

class DebateResponse(BaseModel):
    debate_id: int
    title: str
    proposition_model: str
    opposition_model: str
    debate_state: str

    model_config= {
        'from_attributes':True
    }