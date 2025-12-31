from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from modules.core.token_storage import token_storage
import httpx

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class TokenRequest(BaseModel):
    access_token: str

@router.post("/set-token")
async def set_token(request: TokenRequest):
    try:
        token_storage.set_token(request.access_token)
        print(f"Token received and stored: {request.access_token[:10]}...") # Log first 10 chars for verification
        return {"message": "Token stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-token")
async def test_token():
    """Test endpoint to verify token works by calling cloud API"""
    try:
        token = token_storage.get_token()
        if not token:
            raise HTTPException(status_code=400, detail="No token stored. Please login first.")
        
        # Call cloud API's /api/accounts endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/accounts",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Token is valid",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Cloud API returned status {response.status_code}",
                    "detail": response.text
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
