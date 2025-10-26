"""
Receipt data models based on TabScanner API response.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ReceiptItem(BaseModel):
    """Individual line item from a receipt (based on TabScanner lineItems)"""
    id: str = Field(..., description="Unique identifier for this item (generated)")
    line_number: int = Field(..., description="Position on the receipt (1-indexed)")
    desc_clean: str = Field(..., description="Cleaned product description from TabScanner")
    desc: Optional[str] = Field(None, description="Original product description")
    qty: float = Field(default=1.0, description="Quantity purchased")
    price: float = Field(..., description="Unit price")
    line_total: float = Field(..., description="Total cost for this line item")
    product_code: Optional[str] = Field(None, description="Product code/SKU if available")


class AddressNorm(BaseModel):
    """Normalized address from TabScanner"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None


class Receipt(BaseModel):
    """
    Parsed receipt data from TabScanner.
    Maps TabScanner API response to our internal format.
    """
    # Merchant info
    establishment: Optional[str] = Field(None, description="Business/store name")
    address: Optional[AddressNorm] = Field(None, description="Merchant address")

    # Date/time
    date: Optional[str] = Field(None, description="Purchase timestamp")
    date_iso: Optional[str] = Field(None, description="ISO 8601 formatted date")

    # Line items
    line_items: List[ReceiptItem] = Field(default_factory=list, description="Line items on receipt")

    # Financial totals
    subtotal: float = Field(..., description="Subtotal before tax")
    tax: float = Field(default=0.0, description="Total tax amount")
    tip: float = Field(default=0.0, description="Tip amount")
    discount: float = Field(default=0.0, description="Discount amount if applicable")
    total: float = Field(..., description="Total purchase amount")

    # Currency and payment
    currency: Optional[str] = Field(None, description="Currency code (USD, EUR, etc)")
    payment_method: Optional[str] = Field(None, description="Method of payment used")
    last_four_digits: Optional[str] = Field(None, description="Last 4 digits of card")

    # Confidence metrics
    total_confidence: Optional[float] = Field(None, description="Confidence in total amount (0-1)")
    validated_total: Optional[bool] = Field(None, description="Whether total has been validated")

    # Metadata
    document_type: Optional[str] = Field(None, description="Type of document scanned")

    @classmethod
    def from_tabscanner(cls, tabscanner_result: dict) -> "Receipt":
        """
        Create a Receipt from TabScanner API result.

        Args:
            tabscanner_result: The 'result' object from TabScanner API response

        Returns:
            Receipt instance with processed line items
        """
        # Process line items and assign IDs
        line_items = []
        for idx, item in enumerate(tabscanner_result.get("lineItems", []), start=1):
            # Handle qty=0 from TabScanner (treat as 1.0 for splitting purposes)
            qty = item.get("qty", 1.0)
            if qty == 0:
                qty = 1.0

            receipt_item = ReceiptItem(
                id=f"item_{idx}",
                line_number=idx,
                desc_clean=item.get("descClean", "Unknown Item"),
                desc=item.get("desc"),
                qty=qty,
                price=item.get("price", 0.0),
                line_total=item.get("lineTotal", 0.0),
                product_code=item.get("productCode")
            )
            line_items.append(receipt_item)

        # Process address
        address_data = tabscanner_result.get("addressNorm")
        address = AddressNorm(**address_data) if address_data else None

        return cls(
            establishment=tabscanner_result.get("establishment"),
            address=address,
            date=tabscanner_result.get("date"),
            date_iso=tabscanner_result.get("dateISO"),
            line_items=line_items,
            subtotal=tabscanner_result.get("subTotal", 0.0),
            tax=tabscanner_result.get("tax", 0.0),
            tip=tabscanner_result.get("tip", 0.0),
            discount=tabscanner_result.get("discount", 0.0),
            total=tabscanner_result.get("total", 0.0),
            currency=tabscanner_result.get("currency"),
            payment_method=tabscanner_result.get("paymentMethod"),
            last_four_digits=tabscanner_result.get("lastFourDigits"),
            total_confidence=tabscanner_result.get("totalConfidence"),
            validated_total=tabscanner_result.get("validatedTotal"),
            document_type=tabscanner_result.get("documentType")
        )


class TabScannerResponse(BaseModel):
    """Full TabScanner API response wrapper"""
    status: str
    status_code: int
    success: bool
    code: int
    result: dict  # Raw result object to be processed into Receipt
