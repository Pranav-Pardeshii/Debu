import asyncio

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from app.services import debates_service
from app.database import get_session
from app.services import debates_service
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

# Listen to Human inturruptions 
async def listener(ws: WebSocket, queue: asyncio.Queue):
    while True:
        data = await ws.receive_json()
        await queue.put(data)

@router.websocket("/ws/debates/{debate_id}")
async def debates_ws(websocket: WebSocket, debate_id: int, db : AsyncSession = Depends(get_session)):
    await websocket.accept()
    try: 
        queue = asyncio.Queue()

        listener = await asyncio.create_task(listener(websocket, queue))
        orchestrator = await asyncio.create_task(debates_service.run(debate_id, websocket, db, queue))

        asyncio.gather(listener, orchestrator)
    except WebSocketDisconnect:
        return {"detail":"User diconnected."}
