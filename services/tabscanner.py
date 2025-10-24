"""
TabScanner API integration service.
Handles receipt processing via the TabScanner API.
"""
import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

TABSCANNER_API_KEY = os.environ.get("TABSCANNER_API_KEY", "")


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
