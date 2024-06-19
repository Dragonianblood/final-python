from fastapi import APIRouter, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse
from models.user import User
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@router.post("/register", response_class=HTMLResponse)
async def register(username: str = Form(...), password1: str = Form(...), password2: str = Form(...)):
    if password1 != password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if await User.find_one(User.username == username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password1)
    new_user = User(username=username, password=hashed_password)
    await new_user.insert()
    return HTMLResponse("<h2>Registration successful</h2>")

@router.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    db_user = await User.find_one(User.username == username)
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    response = HTMLResponse("<h2>Login successful</h2>")
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response
