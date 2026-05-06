import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
db = client.grizli_chat
users = db.users

async def get_user(user_id: int):
    return await users.find_one({"_id": user_id})

async def create_user(user_id: int):
    user_data = {
        "_id": user_id,
        "age": None,
        "status": "idle",
        "category": None,
        "last_category": None,
        "partner_id": None,
        "last_activity": datetime.now().isoformat()
    }
    await users.insert_one(user_data)
    return user_data

async def update_user(user_id: int, **kwargs):
    kwargs["last_activity"] = datetime.now().isoformat()
    await users.update_one({"_id": user_id}, {"$set": kwargs})

async def find_partner(user_id: int, category: str, age: int):
    # Base query
    query = {
        "status": "searching",
        "category": category,
        "_id": {"$ne": user_id}
    }
    
    # If it's the 18+ category, partner MUST be adult too
    if category == "✅ Ночной лес (18+)":
        query["age"] = {"$gte": 18}
    
    partner = await users.find_one(query)
    return partner

async def start_chat(user_id1: int, user_id2: int):
    await update_user(user_id1, status="chatting", partner_id=user_id2)
    await update_user(user_id2, status="chatting", partner_id=user_id1)

async def end_chat(user_id: int):
    user = await get_user(user_id)
    if not user or not user.get("partner_id"):
        # Still reset user status just in case they were searching
        await update_user(user_id, status="idle", partner_id=None, category=None)
        return None
    
    partner_id = user["partner_id"]
    
    await update_user(user_id, status="idle", partner_id=None, category=None)
    await update_user(partner_id, status="idle", partner_id=None, category=None)
    
    return partner_id
