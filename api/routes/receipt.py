"""
Receipt upload and processing routes.
Handles receipt image upload and parsing via TabScanner.
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.tabscanner import process_receipt_with_tabscanner, get_receipt_result_with_tabscanner

router = APIRouter(prefix="/api/receipt", tags=["receipt"])


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """Upload a receipt image and get a token for processing"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected image, got {file.content_type}"
        )

    # Validate file size (10MB limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Submit to Tabscanner for processing
        process_data = await process_receipt_with_tabscanner(tmp_path)
        token = process_data.get("token")

        if not token:
            raise HTTPException(status_code=500, detail="No token received from Tabscanner")

        return {
            "token": token,
            "message": "Receipt uploaded successfully. Use the token to poll for results."
        }
    finally:
        os.unlink(tmp_path)


@router.get("/result/{token}")
async def get_receipt_result(token: str):
    """Poll for receipt processing results using the token from upload"""
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    result = await get_receipt_result_with_tabscanner(token)

    # If processing is complete, convert TabScanner result to Receipt object
    if result.get("status") == "done" and result.get("result"):
        from api.models.receipt import Receipt
        receipt = Receipt.from_tabscanner(result["result"])
        return {
            "status": "done",
            "result": receipt.model_dump()
        }

    return result
