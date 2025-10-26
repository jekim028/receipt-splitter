"""
State management service for conversations.
Handles storing and retrieving conversation contexts.
"""
import uuid
from typing import Dict, Optional
from datetime import datetime
from api.models import ConversationContext, AssignmentState, Receipt, Message


class StateManager:
    """Manages conversation state in memory"""

    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}

    def create_conversation(self, receipt: Receipt, people: list[str]) -> ConversationContext:
        """Create a new conversation with initial state"""
        conversation_id = str(uuid.uuid4())

        # Initialize assignment state
        assignment_state = AssignmentState(
            receipt=receipt,
            people=people,
            item_assignments={},
            tax_assignment=None,
            tip_assignment=None
        )

        # Create conversation context
        context = ConversationContext(
            conversation_id=conversation_id,
            assignment_state=assignment_state,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.conversations[conversation_id] = context
        return context

    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)

    def update_conversation(self, conversation_id: str, context: ConversationContext) -> None:
        """Update conversation context"""
        context.updated_at = datetime.now()
        self.conversations[conversation_id] = context

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to the conversation"""
        context = self.get_conversation(conversation_id)
        if context:
            message = Message(role=role, content=content, timestamp=datetime.now())
            context.messages.append(message)
            context.updated_at = datetime.now()

    def update_assignment_state(self, conversation_id: str, assignment_state: AssignmentState) -> None:
        """Update the assignment state for a conversation"""
        context = self.get_conversation(conversation_id)
        if context:
            context.assignment_state = assignment_state
            context.updated_at = datetime.now()

    def set_highlighted_items(self, conversation_id: str, item_ids: list[str]) -> None:
        """Set which items should be highlighted in the UI"""
        context = self.get_conversation(conversation_id)
        if context:
            context.highlighted_items = item_ids
            context.updated_at = datetime.now()


# Global instance (in production, use Redis or a database)
state_manager = StateManager()
