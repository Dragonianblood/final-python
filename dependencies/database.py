from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models.photo import Gallery

from models.photo import Gallery
from models.user import User  # Import the User model

@asynccontextmanager
async def connectToMongodb(app: FastAPI):
    client = AsyncIOMotorClient("mongodb://localhost")
    try:
        await init_beanie(database=client["SMIC"], document_models=[Gallery, User])  # Include User model
        print("INFO: Connected to MongoDB")
        yield
    finally:
        client.close()
        print("INFO: Disconnected from MongoDB")
