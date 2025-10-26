"""
Conversation routes for receipt splitting.
Handles starting conversations, sending messages, and retrieving state.
"""
from fastapi import APIRouter, HTTPException
from api.models import (
    StartConversationRequest,
    StartConversationResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    AssignmentStateResponse,
    ReceiptItem,
    Message,
)
from services.state_manager import state_manager
from services.claude_agent import claude_agent

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """
    Start a new conversation for receipt splitting.

    Accepts a parsed receipt and list of people, creates a new conversation
    with initialized assignment state.
    """
    # Create conversation with initial state
    context = state_manager.create_conversation(
        receipt=request.receipt,
        people=request.people
    )

    # Generate welcome message
    item_count = len(request.receipt.line_items)
    people_names = ", ".join(request.people[:-1]) + f" and {request.people[-1]}" if len(request.people) > 1 else request.people[0]
    merchant = request.receipt.establishment or "this receipt"

    welcome_message = (
        f"I found {item_count} item{'s' if item_count != 1 else ''} on your receipt from {merchant}. "
        f"Ready to split it between {people_names}! "
        f"Just tell me who ordered what, and I'll handle the calculations."
    )

    # Add welcome message to conversation
    state_manager.add_message(
        context.conversation_id,
        role="assistant",
        content=welcome_message
    )

    return StartConversationResponse(
        conversation_id=context.conversation_id,
        message=welcome_message,
        assignment_state=context.assignment_state
    )


@router.post("/{conversation_id}/message", response_model=ChatMessageResponse)
async def send_message(conversation_id: str, request: ChatMessageRequest):
    """
    Send a message in an existing conversation.

    The agent will process the message and update assignments accordingly.
    Currently returns a stub response - will integrate Claude agent later.
    """
    # Get conversation
    context = state_manager.get_conversation(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Add user message
    state_manager.add_message(conversation_id, role="user", content=request.message)

    # Process message with Claude agent
    # The agent will update the context's assignment_state directly
    agent_response, highlighted_items = claude_agent.process_message(
        user_message=request.message,
        context=context
    )

    # Add assistant response
    state_manager.add_message(conversation_id, role="assistant", content=agent_response)

    # Update highlighted items
    state_manager.set_highlighted_items(conversation_id, highlighted_items)

    # Update the assignment state (in case the agent modified it)
    state_manager.update_assignment_state(conversation_id, context.assignment_state)

    # Refresh context
    context = state_manager.get_conversation(conversation_id)

    return ChatMessageResponse(
        message=agent_response,
        assignment_state=context.assignment_state,
        highlighted_items=context.highlighted_items
    )


@router.get("/{conversation_id}/state", response_model=AssignmentStateResponse)
async def get_conversation_state(conversation_id: str):
    """
    Get the current assignment state for a conversation.

    Returns the full assignment state, list of unassigned items,
    and calculated totals per person.
    """
    # Get conversation
    context = state_manager.get_conversation(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get unassigned items
    unassigned_items = context.assignment_state.get_unassigned_items()

    # Calculate totals
    totals = context.assignment_state.calculate_totals()

    return AssignmentStateResponse(
        assignment_state=context.assignment_state,
        unassigned_items=unassigned_items,
        totals=totals
    )


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """
    Get all messages in a conversation.

    Returns the full message history for the conversation.
    """
    # Get conversation
    context = state_manager.get_conversation(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": context.messages
    }


@router.post("/{conversation_id}/confirm")
async def confirm_split(conversation_id: str):
    """
    Finalize the receipt split and generate payment summary.

    Returns final totals and payment instructions (Venmo links, etc).
    """
    # Get conversation
    context = state_manager.get_conversation(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if all items are assigned
    unassigned_items = context.assignment_state.get_unassigned_items()
    if unassigned_items:
        unassigned_names = [item.desc_clean for item in unassigned_items]
        raise HTTPException(
            status_code=400,
            detail=f"Cannot confirm split - these items are unassigned: {', '.join(unassigned_names)}"
        )

    # Calculate final totals
    totals = context.assignment_state.calculate_totals()

    # TODO: Generate Venmo links or payment instructions

    return {
        "conversation_id": conversation_id,
        "status": "confirmed",
        "totals": totals,
        "message": "Split confirmed! Here's what everyone owes."
    }
