import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")
if not MONGO_URL:
    raise ValueError("MONGO_URL is not set in .env")
