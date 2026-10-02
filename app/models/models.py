from datetime import datetime

from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ---- Enum ----

class MessageRole(str, Enum):
    PROPOSITION= "proposition"
    OPPOSITION= "opposition"
    HUMAN= "human"
    SUMMARIZER= "summarizer"

class MessageType(str, Enum):
    DEBATE_TURN= "debate_turn"
    HUMAN_INJECTION= "human_injection"
    SUMMARY= "summary"

class DebateState(str, Enum):
    ACTIVE= "active"
    PAUSED= "paused"
    SUMMARIZING= "summarizing"
    COMPLETE= "complete"


# ---- Model Schemas ----

class Base(DeclarativeBase):
    pass

class Debate(Base):
    __tablename__ = "debates"
    debate_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    proposition_model: Mapped[str] 
    opposition_model: Mapped[str] 
    max_turns: Mapped[int] = mapped_column(default= 6)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(server_default=func.now())
    debate_state: Mapped[DebateState] = mapped_column(SQLAlchemyEnum(DebateState), default= DebateState.ACTIVE)

    messages: Mapped[list["Message"]] = relationship(back_populates= "debate")

class Message(Base):
    __tablename__ = "messages"
    message_id: Mapped[int] = mapped_column(primary_key=True)
    debate_id: Mapped[int] = mapped_column(ForeignKey("debates.debate_id"))
    role: Mapped[MessageRole] = mapped_column(SQLAlchemyEnum(MessageRole))
    message_type: Mapped[MessageType] = mapped_column(SQLAlchemyEnum(MessageType))
    content: Mapped[str] = mapped_column()
    sequence_number: Mapped[int]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
 
    debate: Mapped["Debate"] = relationship(back_populates="messages")
