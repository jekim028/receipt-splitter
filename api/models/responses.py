"""
Response models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Dict
from api.models.assignment import AssignmentState
from api.models.receipt import ReceiptItem


class StartConversationResponse(BaseModel):
    """Response when starting a conversation"""
    conversation_id: str
    message: str
    assignment_state: AssignmentState


class ChatMessageResponse(BaseModel):
    """Response from the agent"""
    message: str
    assignment_state: AssignmentState
    highlighted_items: List[str] = Field(default_factory=list)


class AssignmentStateResponse(BaseModel):
    """Response containing current assignment state"""
    assignment_state: AssignmentState
    unassigned_items: List[ReceiptItem]
    totals: Dict[str, float]
