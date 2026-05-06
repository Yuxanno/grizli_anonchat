from aiogram import Router, F, types
from aiogram.types import Message
from database import get_user, update_user, find_partner, start_chat, end_chat
from keyboards import get_chat_kb, get_main_menu_kb, get_stop_search_kb

router = Router()

CATEGORIES = [
    "✅ IT-берлога", 
    "✅ Ночной лес (18+)", 
    "✅ Игровая пещера", 
    "✅ Подслушано в лесу", 
    "✅ Биржа охотников",
    "✅ Зона дзен"
]

async def execute_search(message: Message, user: dict, category: str):
    if category == "✅ Ночной лес (18+)" and user.get("age", 0) < 18:
        return await message.answer("Маловат еще для этого леса. Охоться в других местах! 🐻")
    
    await update_user(message.from_user.id, status="searching", category=category, last_category=category)
    await message.answer(f"🔍 Жди, ищу тебе достойного зверя в {category}... 🐻", reply_markup=get_stop_search_kb())
    
    partner = await find_partner(message.from_user.id, category, user.get("age"))
    
    if partner:
        await start_chat(message.from_user.id, partner["_id"])
        
        found_msg = "Собеседник в берлоге! Начинай рычать. 🐻🎭"
        await message.answer(found_msg, reply_markup=get_chat_kb())
        
        try:
            await message.bot.send_message(partner["_id"], found_msg, reply_markup=get_chat_kb())
        except Exception:
            await end_chat(partner["_id"])
            await message.answer("Зверь сорвался с крючка... Ищу другого. 🛡")
            # Restart search
            await execute_search(message, user, category)

@router.message(F.text.in_(CATEGORIES))
async def start_searching(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user.get("age") is None:
        return await message.answer("Сначала скажи, сколько тебе зим, охотник! 🐻")
    
    await execute_search(message, user, message.text)

@router.message(F.text == "⚡️ Быстрый поиск")
async def quick_search(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user.get("age") is None:
        return await message.answer("Сначала скажи, сколько тебе зим, охотник! 🐻")
    
    last_category = user.get("last_category")
    if not last_category:
        return await message.answer("Ты еще не охотился ни в одной берлоге. Выбери сначала! 🐻", reply_markup=get_main_menu_kb())
    
    await execute_search(message, user, last_category)

@router.message(F.text == "🔄 Следующий")
async def next_partner(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user["status"] != "chatting":
        return
    
    category = user["category"]
    partner_id = await end_chat(message.from_user.id)
    
    if partner_id:
        try:
            await message.bot.send_message(partner_id, "Собеседник покинул берлогу... 🐻", reply_markup=get_main_menu_kb())
        except Exception:
            pass
            
    await message.answer("Ищу нового зверя... 🛡")
    
    # Re-trigger search logic
    await execute_search(message, user, category)

@router.message()
async def relay_message(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user["status"] != "chatting":
        return
    
    if message.text in ["🔄 Следующий", "🔙 Выход в меню", "🐻 Выбрать берлогу", "👤 Мой профиль", "⚡️ Быстрый поиск"]:
        return

    partner_id = user["partner_id"]
    try:
        # Relay EVERYTHING: text, stickers, photos, voice, etc.
        await message.copy_to(partner_id)
    except Exception:
        await end_chat(message.from_user.id)
        await message.answer("⚠️ Собеседник скрылся в тумане. Возвращайся в меню. 🛡", reply_markup=get_main_menu_kb())
