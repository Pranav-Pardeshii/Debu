from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from app.services import debates_service
from app.database import get_session
from app.services import debates_service
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

@router.websocket("/ws/debates/{debate_id}/")
async def debates_ws(websocket: WebSocket, debate_id: int, db : AsyncSession = Depends(get_session)):
    await websocket.accept()
    try: 
        await debates_service.run(debate_id, websocket, db)
    except WebSocketDisconnect:
        return {"detail":"User diconnected."}
