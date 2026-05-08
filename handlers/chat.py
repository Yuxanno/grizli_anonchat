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

async def execute_search(message: Message, user: dict, categories: list):
    # Ban check
    from datetime import datetime
    if user.get("ban_until"):
        ban_until = datetime.fromisoformat(user["ban_until"])
        if ban_until > datetime.now():
            remaining = ban_until - datetime.now()
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            return await message.answer(f"🛑 Ты временно изгнан из леса. \nОсталось: {mins} мин. {secs} сек. 🐻")

    # Filter 18+ if underage
    if "✅ Ночной лес (18+)" in categories and user.get("age", 0) < 18:
        return await message.answer("Маловат еще для ночного леса. Выбери другие берлоги! 🐻")

    await update_user(message.from_user.id, status="searching", selected_categories=categories)
    
    cats_str = ", ".join(categories)
    await message.answer(f"🔍 Жди, ищу тебе достойного зверя в берлогах: {cats_str}... 🐻", reply_markup=get_stop_search_kb())
    
    partner = await find_partner(
        message.from_user.id, 
        categories, 
        user.get("gender"), 
        user.get("target_gender", "Any")
    )
    
    if partner:
        # Find overlapping categories to show which one matched
        common_cats = list(set(categories) & set(partner.get("selected_categories", [])))
        match_cat = common_cats[0] if common_cats else categories[0]
        
        await start_chat(message.from_user.id, partner["_id"])
        
        gender_icon = "🧔" if partner.get("gender") == "M" else "👩"
        partner_info = f"{gender_icon} {partner.get('age')} лет, берлога: {match_cat}"
        
        found_msg = f"Зверь найден! 🐾\n👤 **{partner_info}**\n\nНачинай рычать. 🐻🎭"
        await message.answer(found_msg, reply_markup=get_chat_kb(), parse_mode="Markdown")
        
        # Notify partner too
        our_gender_icon = "🧔" if user.get("gender") == "M" else "👩"
        our_info = f"{our_gender_icon} {user.get('age')} лет, берлога: {match_cat}"
        partner_found_msg = f"Зверь найден! 🐾\n👤 **{our_info}**\n\nНачинай рычать. 🐻🎭"
        
        try:
            await message.bot.send_message(partner["_id"], partner_found_msg, reply_markup=get_chat_kb(), parse_mode="Markdown")
        except Exception:
            await end_chat(partner["_id"])
            await message.answer("Зверь сорвался с крючка... Ищу другого. 🛡")
            await execute_search(message, user, categories)

@router.callback_query(F.data.startswith("toggle_cat_"))
async def process_toggle_cat(callback: types.CallbackQuery):
    cat = callback.data.replace("toggle_cat_", "")
    user = await get_user(callback.from_user.id)
    selected = user.get("selected_categories", [])
    
    if cat in selected:
        selected.remove(cat)
    else:
        selected.append(cat)
    
    await update_user(callback.from_user.id, selected_categories=selected)
    
    from keyboards import get_categories_kb
    try:
        await callback.message.edit_reply_markup(reply_markup=get_categories_kb(selected))
    except Exception:
        pass # Message hasn't changed
    await callback.answer()

@router.callback_query(F.data == "start_search_multi")
async def process_start_search(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    selected = user.get("selected_categories", [])
    
    if not selected:
        return await callback.answer("Выбери хотя бы одну берлогу! 🐻", show_alert=True)
    
    await callback.message.delete()
    await execute_search(callback.message, user, selected)
    await callback.answer()

@router.message(F.text == "⚡️ Быстрый поиск")
async def quick_search(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user.get("age") is None:
        return await message.answer("Сначала скажи, сколько тебе зим, охотник! 🐻")
    
    selected = user.get("selected_categories", [])
    if not selected:
        return await message.answer("Ты еще не выбрал ни одной берлоги. Выбери сначала! 🐻", reply_markup=get_main_menu_kb())
    
    await execute_search(message, user, selected)

@router.message(F.text == "🔄 Следующий")
async def next_partner(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user["status"] != "chatting":
        return
    
    selected_cats = user.get("selected_categories", [])
    partner_id = await end_chat(message.from_user.id)
    
    if partner_id:
        from keyboards import get_rating_kb
        try:
            await message.bot.send_message(partner_id, "Собеседник покинул берлогу... Оцени его: 🐻", reply_markup=get_rating_kb(message.from_user.id))
        except Exception:
            pass
            
    await message.answer("Ищу нового зверя... 🛡")
    await execute_search(message, user, selected_cats)

@router.message(F.text == "👤 Поделиться профилем")
async def share_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user["status"] != "chatting":
        return
    
    username = message.from_user.username
    if username:
        text = f"👤 Собеседник поделился контактом: @{username}"
    else:
        text = f"👤 Собеседник поделился профилем: [ссылка](tg://user?id={message.from_user.id})"
    
    try:
        await message.bot.send_message(user["partner_id"], text, parse_mode="Markdown")
        await message.answer("✅ Твой профиль отправлен собеседнику!")
    except Exception:
        pass

@router.message()
async def relay_message(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user["status"] != "chatting":
        return
    
    if message.text in ["🔄 Следующий", "🔙 Выход в меню", "🐻 Выбрать берлогу", "👤 Мой профиль", "⚡️ Быстрый поиск", "👤 Поделиться профилем"]:
        return

    # Moderation
    full_text = (message.text or "") + (message.caption or "")
    
    is_violation = False
    warning_msg = ""
    
    if "@" in full_text:
        is_violation = True
        warning_msg = "⚠️ Сообщения с @ запрещены! Сообщение не отправлено. Бан будет выдан после чата."
    elif "_" in full_text:
        from datetime import datetime
        start_time = datetime.fromisoformat(user["chat_started_at"])
        if (datetime.now() - start_time).total_seconds() < 15:
            is_violation = True
            warning_msg = "⚠️ Сообщения с _ запрещены в первые 15 секунд! Бан будет выдан после чата."

    if is_violation:
        violations = user.get("violations_count", 0) + 1
        ban_duration = 60 if violations < 5 else 300
        await update_user(message.from_user.id, 
                         violations_count=violations, 
                         pending_ban_seconds=ban_duration)
        return await message.answer(warning_msg)

    partner_id = user["partner_id"]
    try:
        await message.copy_to(partner_id)
    except Exception:
        from keyboards import get_rating_kb
        await end_chat(message.from_user.id)
        await message.answer("⚠️ Собеседник скрылся в тумане. Оцени его: 🛡", reply_markup=get_rating_kb(partner_id))
        await message.answer("Возвращайся на опушку. 🐻", reply_markup=get_main_menu_kb())
