from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List, Literal, Union

from . import ALL_MODELS


class MessageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: Literal["user", "assistant"] = "user"
    content: Union[str, dict]


class Message(MessageCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class ChatModel(BaseModel):
    model: Literal[ALL_MODELS] = "gpt-4-1106-preview"


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = False


class UserCreate(UserBase):
    password: str  # plain password


class UserAdminCreate(UserCreate):
    role: Literal["admin"] = "admin"


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: Literal["user", "admin"]


class UserInDB(User):
    model_config = ConfigDict(from_attributes=True)

    password: str  # hashed password
