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
        "gender": None,
        "target_gender": "Any",
        "status": "idle",
        "category": None,
        "selected_categories": [],
        "partner_id": None,
        "last_partner_id": None,
        "last_activity": datetime.now().isoformat(),
        # Moderation fields
        "violations_count": 0,
        "ad_reports_count": 0,
        "scam_reports_count": 0,
        "ban_until": None,
        "pending_ban_seconds": 0,
        "chat_started_at": None
    }
    await users.insert_one(user_data)
    return user_data

async def update_user(user_id: int, **kwargs):
    kwargs["last_activity"] = datetime.now().isoformat()
    await users.update_one({"_id": user_id}, {"$set": kwargs})

async def find_partner(user_id: int, categories: list, gender: str, target_gender: str):
    now = datetime.now().isoformat()
    query = {
        "status": "searching",
        "selected_categories": {"$in": categories},
        "_id": {"$ne": user_id},
        "$or": [
            {"ban_until": None},
            {"ban_until": {"$lt": now}}
        ]
    }
    
    if target_gender != "Any":
        query["gender"] = target_gender
    
    query["target_gender"] = {"$in": [gender, "Any"]}
    
    partner = await users.find_one(query)
    return partner

async def start_chat(user_id1: int, user_id2: int):
    now = datetime.now().isoformat()
    await update_user(user_id1, status="chatting", partner_id=user_id2, chat_started_at=now, pending_ban_seconds=0)
    await update_user(user_id2, status="chatting", partner_id=user_id1, chat_started_at=now, pending_ban_seconds=0)

async def end_chat(user_id: int):
    user = await get_user(user_id)
    if not user or not user.get("partner_id"):
        # Reset searching status
        await update_user(user_id, status="idle", partner_id=None, category=None)
        return None
    
    partner_id = user["partner_id"]
    partner = await get_user(partner_id)

    # Process delayed bans
    from datetime import timedelta
    
    for u_id, u_data in [(user_id, user), (partner_id, partner)]:
        if u_data and u_data.get("pending_ban_seconds", 0) > 0:
            ban_time = datetime.now() + timedelta(seconds=u_data["pending_ban_seconds"])
            await update_user(u_id, ban_until=ban_time.isoformat(), pending_ban_seconds=0)

    await update_user(user_id, status="idle", partner_id=None, category=None, last_partner_id=partner_id)
    await update_user(partner_id, status="idle", partner_id=None, category=None, last_partner_id=user_id)
    
    return partner_id
