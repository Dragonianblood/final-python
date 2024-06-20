# dependencies/auth.py

from fastapi import Request, HTTPException, Cookie
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Example: token expires in 30 minutes


def verify_jwt_cookie(access_token: str = Cookie(None)):
    if access_token is None:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
def sign_jwt(user_id: str) -> str:
    """
    Create a JWT token for authentication.
    :param user_id: Unique identifier for the user
    :return: JWT token as a string
    """
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
