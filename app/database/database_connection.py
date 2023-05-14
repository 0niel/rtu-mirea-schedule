from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import MONGODB_URL
from .database import db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(MONGODB_URL)


async def close_mongo_connection():
    db.client.close()
