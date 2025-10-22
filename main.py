from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import httpx
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Receipt Splitter API")

TABSCANNER_API_KEY = os.environ.get("TABSCANNER_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# In-memory storage (for testing only)
conversations = {}


# ==============================================
# MODELS
# ==============================================
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


# ==============================================
# HELPER FUNCTIONS
# ==============================================
async def process_receipt_with_tabscanner(image_path: str):
    """Process receipt using Tabscanner - returns token for polling"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(image_path, "rb") as f:
                files = {"receipt": f}
                headers = {"apikey": TABSCANNER_API_KEY}
                response = await client.post(
                    "https://api.tabscanner.com/api/2/process",
                    headers=headers,
                    files=files,
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Tabscanner processing error: {response.text}"
                )

            data = response.json()
            return data
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tabscanner request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Failed to reach Tabscanner: {str(e)}")


async def get_receipt_result_with_tabscanner(token: str):
    """Get result of Tabscanner processed receipt"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"apikey": TABSCANNER_API_KEY}
            response = await client.get(
                f"https://api.tabscanner.com/api/result/{token}",
                headers=headers,
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Tabscanner result error: {response.text}"
            )

        data = response.json()
        return data
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tabscanner request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Failed to reach Tabscanner: {str(e)}")


# ==============================================
# API ENDPOINTS
# ==============================================


@app.post("/api/receipt/upload")
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


@app.get("/api/receipt/result/{token}")
async def get_receipt_result(token: str):
    """Poll for receipt processing results using the token from upload"""
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    result = await get_receipt_result_with_tabscanner(token)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
