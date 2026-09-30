from sqlalchemy import select
from app.providers.factory import get_provider
from app.prompts import PROPOSITION_PROMPT, OPPOSITION_PROMPT

from fastapi import WebSocketDisconnect

from app.models.models import Debate, Message, DebateState, MessageType, MessageRole

async def get_debate_history(debate_id, db):
    result = await db.execute(select(Message).where(Message.debate_id==debate_id).order_by(Message.sequence_number))
    history = result.scalars().all()
    return history    


async def run(debate_id, websocket, db):
    result = await db.execute(select(Debate).where(Debate.debate_id==debate_id))
    debate_metadata = result.scalar_one_or_none()
    if not debate_metadata:
        await websocket.close(code=4004)
        return 
    proposition_provider = get_provider(debate_metadata.proposition_model)
    opposition_provider = get_provider(debate_metadata.opposition_model)

    current_speaker = "proposition"

    while True:
        try:
            full_response = ''
            history = await get_debate_history(debate_id=debate_id, db=db)
            if current_speaker == "proposition":
                async for chunk in proposition_provider.generate_response(history = history, current_speaker= current_speaker, system_instruction= PROPOSITION_PROMPT):
                    full_response += chunk
                    await websocket.send_text(chunk)
            elif current_speaker == "opposition":
                async for chunk in opposition_provider.generate_response(history=history, current_speaker=current_speaker, system_instruction= OPPOSITION_PROMPT):
                    full_response += chunk
                    await websocket.send_text(chunk)
            message_type = MessageType.DEBATE_TURN
            role = MessageRole.OPPOSITION if current_speaker == "opposition" else MessageRole.PROPOSITION
            message_entry = Message(debate_id=debate_id, role=role, message_type=message_type, content=full_response, sequence_number= history[-1].sequence_number+1 )

            db.add(message_entry)
            await db.commit()
            await db.refresh(message_entry)

            current_speaker = "opposition" if current_speaker == "proposition" else "proposition"
        except WebSocketDisconnect:
            break