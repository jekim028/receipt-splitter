"""
Claude agent service for processing receipt splitting conversations.
Uses Claude's function calling to manage item assignments.
"""

import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from api.models import (
    ConversationContext,
    AssignmentState,
    ItemAssignment,
    SplitStrategy,
    ReceiptItem,
)


class ClaudeAgent:
    """AI agent for processing receipt splitting requests"""

    def __init__(self):
        self.client = None
        self.model = "claude-haiku-4-5-20251001"

    def _ensure_client(self):
        """Lazily initialize the Anthropic client"""
        if self.client is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key or api_key == "your-anthropic-api-key-here":
                raise ValueError(
                    "ANTHROPIC_API_KEY not found or not set. "
                    "Please add your Anthropic API key to the .env file."
                )
            self.client = Anthropic(api_key=api_key)

    def _build_tools(self) -> List[Dict[str, Any]]:
        """Define the function tools available to the agent"""
        return [
            {
                "name": "assign_items",
                "description": "Assign one or more items to specific people. Use this when the user tells you who ordered what.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of item IDs to assign",
                        },
                        "people": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of people names to assign the items to",
                        },
                        "split_strategy": {
                            "type": "string",
                            "enum": ["equal", "proportional", "custom"],
                            "description": "How to split the cost among the people",
                            "default": "equal",
                        },
                    },
                    "required": ["item_ids", "people"],
                },
            },
            {
                "name": "unassign_items",
                "description": "Remove assignments from items. Use this when the user changes their mind or corrects an assignment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of item IDs to unassign",
                        }
                    },
                    "required": ["item_ids"],
                },
            },
            {
                "name": "assign_tax",
                "description": "Assign tax to specific people or split it among everyone.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "people": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of people names to split the tax among",
                        },
                        "split_strategy": {
                            "type": "string",
                            "enum": ["equal", "proportional"],
                            "description": "How to split the tax",
                            "default": "equal",
                        },
                    },
                    "required": ["people"],
                },
            },
            {
                "name": "assign_tip",
                "description": "Assign tip to specific people or split it among everyone.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "people": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of people names to split the tip among",
                        },
                        "split_strategy": {
                            "type": "string",
                            "enum": ["equal", "proportional"],
                            "description": "How to split the tip",
                            "default": "equal",
                        },
                    },
                    "required": ["people"],
                },
            },
            {
                "name": "highlight_items",
                "description": "Highlight specific items in the UI to draw user attention.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of item IDs to highlight",
                        }
                    },
                    "required": ["item_ids"],
                },
            },
            {
                "name": "get_unassigned_items",
                "description": "Get the list of items that haven't been assigned to anyone yet.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build the system prompt with current state context"""
        receipt = context.assignment_state.receipt
        people = context.assignment_state.people
        assignments = context.assignment_state.item_assignments

        # Format receipt items
        items_text = "\n".join(
            [
                f"- ID: {item.id} | Line {item.line_number}: {item.desc_clean} - ${item.line_total:.2f}"
                for item in receipt.line_items
            ]
        )

        # Format current assignments
        assignments_text = ""
        if assignments:
            assignments_text = "\n".join(
                [
                    f"- {assignment.item_id}: assigned to {', '.join(assignment.assigned_to)} ({assignment.split_strategy})"
                    for assignment in assignments.values()
                    if assignment.assigned_to
                ]
            )
        else:
            assignments_text = "None yet"

        # Get unassigned items
        unassigned = context.assignment_state.get_unassigned_items()
        unassigned_text = (
            "\n".join(
                [f"- {item.desc_clean} (${item.line_total:.2f})" for item in unassigned]
            )
            if unassigned
            else "All items assigned!"
        )

        # Tax and tip status
        tax_status = "Not assigned"
        if (
            context.assignment_state.tax_assignment
            and context.assignment_state.tax_assignment.assigned_to
        ):
            tax_status = f"Assigned to {', '.join(context.assignment_state.tax_assignment.assigned_to)}"

        tip_status = "Not assigned"
        if (
            context.assignment_state.tip_assignment
            and context.assignment_state.tip_assignment.assigned_to
        ):
            tip_status = f"Assigned to {', '.join(context.assignment_state.tip_assignment.assigned_to)}"

        return f"""You are a helpful receipt-splitting assistant. Your job is to help users split a receipt fairly between multiple people.

**Receipt Details:**
Merchant: {receipt.establishment or "Unknown"}
Date: {receipt.date or "Unknown"}
Total: ${receipt.total:.2f}
Tax: ${receipt.tax:.2f}
Tip: ${receipt.tip:.2f}
Subtotal: ${receipt.subtotal:.2f}

**Items on Receipt:**
{items_text}

**People Splitting:**
{", ".join(people)}

**Current Assignments:**
{assignments_text}

**Unassigned Items:**
{unassigned_text}

**Tax Status:** {tax_status}
**Tip Status:** {tip_status}

**Your Capabilities:**
You have access to function tools to manage assignments:
- `assign_items`: Assign items to people
- `unassign_items`: Remove assignments
- `assign_tax`: Assign tax
- `assign_tip`: Assign tip
- `highlight_items`: Highlight items in the UI for clarity
- `get_unassigned_items`: Check what's still unassigned

**Guidelines:**
1. **Understand natural language**: Users will say things like "I had the burger" or "split the appetizers between everyone". Parse these requests and call the appropriate functions.

2. **Match items smartly**: Use fuzzy matching when users don't use exact item names. If someone says "burger" and there are multiple burgers, highlight them all and ask for clarification.

3. **Be proactive**: After each assignment, check if there are unassigned items. Gently remind users about unassigned items and ask how to handle them.

4. **Handle tax and tip**: By default, suggest splitting tax and tip proportionally to what each person ordered, or equally if requested.

5. **Confirm actions**: When you assign items, confirm what you did in a friendly way. Example: "Got it, marking the pizza for you and Sarah."

6. **Use visual cues**: Call `highlight_items` when asking about specific items to help users see what you're referring to.

7. **Reference items clearly**: When there's ambiguity, reference items by their names AND positions (line numbers) from the receipt.

8. **Be conversational**: You're a helpful assistant, not a robot. Be friendly, acknowledge what users say, and help them complete the split efficiently.

**Important**: ALWAYS call functions to make changes. Don't just describe what should happen - actually call the function tools to update the state."""

    def _execute_function(
        self,
        function_name: str,
        function_args: Dict[str, Any],
        context: ConversationContext,
        highlighted_items: List[str],
    ) -> str:
        """Execute a function call and update the context"""
        try:
            if function_name == "assign_items":
                item_ids = function_args["item_ids"]
                people = function_args["people"]
                split_strategy = SplitStrategy(
                    function_args.get("split_strategy", "equal")
                )

                # Validate item IDs exist
                valid_item_ids = [
                    item.id for item in context.assignment_state.receipt.line_items
                ]
                invalid_ids = [id for id in item_ids if id not in valid_item_ids]
                if invalid_ids:
                    return f"Error: Invalid item IDs: {invalid_ids}"

                # Validate people exist
                invalid_people = [
                    p for p in people if p not in context.assignment_state.people
                ]
                if invalid_people:
                    return f"Error: Unknown people: {invalid_people}"

                # Create assignments
                for item_id in item_ids:
                    context.assignment_state.item_assignments[item_id] = ItemAssignment(
                        item_id=item_id,
                        assigned_to=people,
                        split_strategy=split_strategy,
                    )

                return f"Successfully assigned items {item_ids} to {people}"

            elif function_name == "unassign_items":
                item_ids = function_args["item_ids"]
                for item_id in item_ids:
                    if item_id in context.assignment_state.item_assignments:
                        del context.assignment_state.item_assignments[item_id]
                return f"Successfully unassigned items {item_ids}"

            elif function_name == "assign_tax":
                people = function_args["people"]
                split_strategy = SplitStrategy(
                    function_args.get("split_strategy", "equal")
                )

                invalid_people = [
                    p for p in people if p not in context.assignment_state.people
                ]
                if invalid_people:
                    return f"Error: Unknown people: {invalid_people}"

                context.assignment_state.tax_assignment = ItemAssignment(
                    item_id="tax", assigned_to=people, split_strategy=split_strategy
                )
                return f"Successfully assigned tax to {people}"

            elif function_name == "assign_tip":
                people = function_args["people"]
                split_strategy = SplitStrategy(
                    function_args.get("split_strategy", "equal")
                )

                invalid_people = [
                    p for p in people if p not in context.assignment_state.people
                ]
                if invalid_people:
                    return f"Error: Unknown people: {invalid_people}"

                context.assignment_state.tip_assignment = ItemAssignment(
                    item_id="tip", assigned_to=people, split_strategy=split_strategy
                )
                return f"Successfully assigned tip to {people}"

            elif function_name == "highlight_items":
                item_ids = function_args["item_ids"]
                highlighted_items.clear()
                highlighted_items.extend(item_ids)
                return f"Highlighted items {item_ids}"

            elif function_name == "get_unassigned_items":
                unassigned = context.assignment_state.get_unassigned_items()
                if not unassigned:
                    return "All items are assigned!"
                items_list = [
                    f"{item.desc_clean} (${item.line_total:.2f})" for item in unassigned
                ]
                return f"Unassigned items: {', '.join(items_list)}"

            else:
                return f"Error: Unknown function {function_name}"

        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"

    def process_message(
        self, user_message: str, context: ConversationContext
    ) -> tuple[str, List[str]]:
        """
        Process a user message and return the agent's response.

        Returns:
            tuple[str, List[str]]: (agent_response, highlighted_item_ids)
        """
        # Ensure client is initialized
        self._ensure_client()

        # Build messages for Claude
        messages = []

        # Add conversation history (excluding system messages)
        for msg in context.messages:
            if msg.role in ["user", "assistant"]:
                messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Track highlighted items
        highlighted_items = []

        # Call Claude with function calling
        try:
            system_prompt = self._build_system_prompt(context)
            tools = self._build_tools()

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            # Process function calls in a loop (agentic loop)
            max_iterations = 10
            iteration = 0

            while iteration < max_iterations:
                # Check if we're done
                if response.stop_reason == "end_turn":
                    # Extract text response
                    text_response = ""
                    for block in response.content:
                        if block.type == "text":
                            text_response += block.text
                    return (
                        text_response or "I've updated the assignments.",
                        highlighted_items,
                    )

                # Process function calls
                if response.stop_reason == "tool_use":
                    # Add assistant response to messages
                    messages.append({"role": "assistant", "content": response.content})

                    # Execute each tool call
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = self._execute_function(
                                block.name, block.input, context, highlighted_items
                            )
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": result,
                                }
                            )

                    # Add tool results to messages
                    messages.append({"role": "user", "content": tool_results})

                    # Continue conversation with Claude
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=4096,
                        system=system_prompt,
                        tools=tools,
                        messages=messages,
                    )

                    iteration += 1
                else:
                    # Unexpected stop reason
                    break

            # If we exit the loop, extract any text response
            text_response = ""
            for block in response.content:
                if block.type == "text":
                    text_response += block.text

            return text_response or "I've processed your request.", highlighted_items

        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}", []


# Global instance
claude_agent = ClaudeAgent()
