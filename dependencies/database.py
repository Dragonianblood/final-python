from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models import photo

@asynccontextmanager
async def connectToMongodb(app: FastAPI):
    client = AsyncIOMotorClient("mongodb://localhost")
    await init_beanie(database=client["SMIC"], document_models=[photo.Gallery])
    print("INFO:   Connected to MongoDB")
    yield
    client.close()
    print("INFO:   Disconnected from MongoDB")
