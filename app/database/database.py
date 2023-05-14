from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


def get_database() -> AsyncIOMotorClient:
    return db.client
