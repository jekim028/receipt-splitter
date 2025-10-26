"""
Request models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List
from api.models.receipt import Receipt


class StartConversationRequest(BaseModel):
    """Request to start a new conversation"""
    receipt: Receipt
    people: List[str] = Field(..., min_length=2, description="Names of people splitting")


class ChatMessageRequest(BaseModel):
    """Request to send a message in a conversation"""
    message: str
