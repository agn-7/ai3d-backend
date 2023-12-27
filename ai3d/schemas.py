from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List, Literal

from . import ALL_MODELS


class MessageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: Literal["human", "ai"] = "human"
    content: str


class Message(MessageCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class ChatModel(BaseModel):
    model: Literal[ALL_MODELS] = "gpt-4"


class Instruction(BaseModel):
    role: Literal["system"] = "system"
    prompt: str = "You are an assistant."


class Settings(ChatModel, Instruction):
    pass


class InteractionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    settings: Settings


class Interaction(InteractionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
