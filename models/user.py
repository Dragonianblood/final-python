from beanie import Document
from pydantic import BaseModel

class User(Document):
    username: str
    password: str

    class Settings:
        name = "users"

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
