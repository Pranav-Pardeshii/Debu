from fastapi import Depends, FastAPI
from app.api.routes.title_generator import generate_title
from app.models.models import Debate
from app.providers.factory import get_provider
from app.schemas.debates_schema import CreateDebateRequest, DebateResponse
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session

router = APIRouter()

@router.post("/debates/", response_model=DebateResponse)
async def new_debate(debate_request: CreateDebateRequest, db : AsyncSession = Depends(get_session)):
    try:
        title = await generate_title(debate_request.topic)
        debate_entry = Debate(**debate_request.model_dump(exclude={"topic"}), title=title)
    
        db.add(debate_entry)
        await db.commit()
        await db.refresh(debate_entry)
        return debate_entry

        
    except Exception as e:
        raise RuntimeError(f"[Error while creating debate]:{e}")