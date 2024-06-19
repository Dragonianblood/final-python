from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

SECRET_KEY = "123456789"  # Replace with your secret key

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = jwt.decode(jwtoken, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
        return True

def sign_jwt(user_id: str):
    payload = {
        "user_id": user_id,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
