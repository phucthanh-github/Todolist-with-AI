from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_helper = Database()

def get_db():
    return db_helper.db

def get_client():
    return db_helper.client

async def connect_to_mongo():
    db_helper.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_helper.db = db_helper.client[settings.MONGODB_DB_NAME]
    
    # Simple check connection
    try:
        await db_helper.client.admin.command('ping')
        print(f"Successfully connected to MongoDB at: {settings.MONGODB_URL.split('@')[-1] if '@' in settings.MONGODB_URL else settings.MONGODB_URL}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Please check if MongoDB is running and settings.MONGODB_URL is correct.")

async def close_mongo_connection():
    if db_helper.client:
        db_helper.client.close()
        print("MongoDB connection closed")
