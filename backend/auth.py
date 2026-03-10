import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from jose import jwt

API_KEY_HEADER = APIKeyHeader(name="Authorization")

DEVICE_API_KEY = os.getenv("DEVICE_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != DEVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

def create_token(user_id: str):
    payload = {"sub": user_id}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
