from sqlalchemy import select, update
from app.providers.factory import get_provider
from app.prompts import PROPOSITION_PROMPT, OPPOSITION_PROMPT

from fastapi import WebSocketDisconnect

from app.models.models import Debate, Message, MessageType, MessageRole, DebateState

async def get_debate_history(debate_id, db):
    result = await db.execute(select(Message).where(Message.debate_id==debate_id).order_by(Message.sequence_number))
    history = result.scalars().all()
    return history    


async def run(debate_id, websocket, db, queue):

    result = await db.execute(select(Debate).where(Debate.debate_id==debate_id))
    debate_metadata = result.scalar_one_or_none()

    if debate_metadata.debate_state == DebateState.COMPLETE:
        await websocket.send_text("__DEBATE_COMPLETE__")
        await websocket.close()
        return

    if not debate_metadata:
        await websocket.close(code=4004)
        return 
    
    proposition_provider = get_provider(debate_metadata.proposition_model)
    opposition_provider = get_provider(debate_metadata.opposition_model)

    history = await get_debate_history(debate_id=debate_id, db=db)
    last_role = history[-1].role if history else None

    if last_role == 'proposition':
        current_speaker = 'opposition'
    elif last_role == 'opposition':
        current_speaker = 'proposition'
    else:
        current_speaker = 'proposition'
    max_turns = debate_metadata.max_turns

    ended_naturally = False

    while True:
        try:
            if not queue.empty():
                msg = await queue.get()
                if msg["type"] == "extend_turns":
                    max_turns += msg["additional_turns"]
                    await db.execute(update(Debate).where(Debate.debate_id==debate_id).values(max_turns=max_turns))
                    await db.commit()
                    continue

                elif msg["type"] == "human_interruption":
                    human_message = Message(
                        debate_id= debate_id,
                        role= MessageRole.HUMAN,
                        content= msg["content"],
                        message_type= MessageType.HUMAN_INJECTION,
                        sequence_number= history[-1].sequence_number + 1
                    )
                    db.add(human_message)
                    await db.commit()
                    history = get_debate_history(debate_id= debate_id, db= db)
                    continue

                elif msg["type"] == "pause":
                    await db.execute(update(Debate).where(Debate.debate_id==debate_id).values(debate_state=DebateState.PAUSED))
                    await db.commit()
                    break
                    
            full_response = ''
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
            message_entry = Message(
                debate_id=debate_id, 
                role=role, 
                message_type=message_type, 
                content=full_response, 
                sequence_number= history[-1].sequence_number+1 
            )

            db.add(message_entry)
            await db.commit()
            await db.refresh(message_entry)

            history = await get_debate_history(debate_id=debate_id, db=db)
            current_speaker = "opposition" if current_speaker == "proposition" else "proposition"

            if history[-1].sequence_number >= max_turns:
                ended_naturally = True
                break
        except WebSocketDisconnect:
            break

    if ended_naturally:
        debate_metadata.debate_state = DebateState.COMPLETE
        await db.commit()
        await websocket.send_text("__DEBATE_COMPLETE__")