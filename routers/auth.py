from fastapi import APIRouter, HTTPException, Form, Depends, Request, Cookie, Response
from fastapi.security import OAuth2PasswordRequestForm
from dependencies.auth import sign_jwt
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.user import User, UserLogin
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
SECRET_KEY = "1234567890"  # Replace with your actual secret key

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

@router.post("/register", response_class=RedirectResponse)
async def register(request: Request, username: str = Form(...), password1: str = Form(...), password2: str = Form(...)):
    if password1 != password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if await User.find_one(User.username == username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password1)
    new_user = User(username=username, password=hashed_password, images=0)
    await new_user.insert()

    db_user = await User.find_one(User.username == username)
    if not db_user or not verify_password(password1, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = sign_jwt(str(db_user.id))
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.post("/login")
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await User.find_one(User.username == form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = sign_jwt(str(db_user.id))
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response
