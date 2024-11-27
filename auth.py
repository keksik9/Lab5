from fastapi import HTTPException, Header
from dotenv import load_dotenv
import os

load_dotenv()

auth_token = os.getenv("AUTH_TOKEN")

def verify_token(token: str = Header(...)):
    if token != auth_token:
        raise HTTPException(status_code=401, detail="unauthorized")