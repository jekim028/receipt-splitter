"""
Conversation models for managing chat sessions.
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from api.models.assignment import AssignmentState


class Message(BaseModel):
    """A single message in the conversation"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationContext(BaseModel):
    """Full context of a conversation session"""
    conversation_id: str
    assignment_state: AssignmentState
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    highlighted_items: List[str] = Field(
        default_factory=list,
        description="Item IDs currently highlighted in UI"
    )
