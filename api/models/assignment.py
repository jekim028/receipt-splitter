"""
Assignment models for tracking how items are split between people.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from api.models.receipt import Receipt, ReceiptItem


class SplitStrategy(str, Enum):
    """How an item should be split between people"""
    EQUAL = "equal"  # Split evenly
    PROPORTIONAL = "proportional"  # Based on what each person ordered
    CUSTOM = "custom"  # Custom split percentages


class ItemAssignment(BaseModel):
    """Assignment of an item to one or more people"""
    item_id: str
    assigned_to: List[str] = Field(default_factory=list, description="List of person names")
    split_strategy: SplitStrategy = Field(default=SplitStrategy.EQUAL)


class AssignmentState(BaseModel):
    """Current state of how items are assigned to people"""
    receipt: Receipt
    people: List[str] = Field(..., description="Names of people splitting the bill")
    item_assignments: Dict[str, ItemAssignment] = Field(
        default_factory=dict,
        description="Map of item_id to assignment"
    )
    tax_assignment: Optional[ItemAssignment] = Field(None, description="How tax is split")
    tip_assignment: Optional[ItemAssignment] = Field(None, description="How tip is split")

    def get_unassigned_items(self) -> List[ReceiptItem]:
        """Get list of items that haven't been assigned to anyone"""
        return [
            item for item in self.receipt.line_items
            if item.id not in self.item_assignments or
            not self.item_assignments[item.id].assigned_to
        ]

    def calculate_totals(self) -> Dict[str, float]:
        """Calculate how much each person owes"""
        totals = {person: 0.0 for person in self.people}

        # Calculate item totals
        for item in self.receipt.line_items:
            if item.id in self.item_assignments:
                assignment = self.item_assignments[item.id]
                if assignment.assigned_to:
                    split_amount = item.line_total / len(assignment.assigned_to)
                    for person in assignment.assigned_to:
                        totals[person] += split_amount

        # Add tax
        if self.tax_assignment and self.tax_assignment.assigned_to:
            tax_split = self.receipt.tax / len(self.tax_assignment.assigned_to)
            for person in self.tax_assignment.assigned_to:
                totals[person] += tax_split

        # Add tip
        if self.tip_assignment and self.tip_assignment.assigned_to:
            tip_split = self.receipt.tip / len(self.tip_assignment.assigned_to)
            for person in self.tip_assignment.assigned_to:
                totals[person] += tip_split

        return totals
