from aiogram import Router, F, types
from database import get_user, update_user
from datetime import datetime, timedelta

router = Router()

@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: types.CallbackQuery):
    # Format: rate_{type}_{partner_id}
    data = callback.data.split("_")
    rate_type = data[1]
    partner_id = int(data[2])
    
    partner = await get_user(partner_id)
    if not partner:
        return await callback.answer("Зверь уже скрылся в тумане...")
    
    await callback.message.edit_text("Спасибо за отзыв! Твой вклад помогает лесу быть чище. 🐻")
    
    if rate_type == "ad":
        count = partner.get("ad_reports_count", 0) + 1
        await update_user(partner_id, ad_reports_count=count)
        
        # Every 2 reports = 5 min ban
        if count % 2 == 0:
            ban_time = datetime.now() + timedelta(minutes=5)
            await update_user(partner_id, ban_until=ban_time.isoformat())
            try:
                await callback.bot.send_message(partner_id, "🛑 Ты получил слишком много жалоб за рекламу. Бан на 5 минут.")
            except: pass
            
    elif rate_type == "scam":
        count = partner.get("scam_reports_count", 0) + 1
        await update_user(partner_id, scam_reports_count=count)
        
        # 3 reports = 10 min, 6 reports = 1 hour
        if count == 3:
            ban_time = datetime.now() + timedelta(minutes=10)
            await update_user(partner_id, ban_until=ban_time.isoformat())
            try:
                await callback.bot.send_message(partner_id, "🛑 На тебя поступили жалобы за скам. Бан на 10 минут.")
            except: pass
        elif count == 6:
            ban_time = datetime.now() + timedelta(hours=1)
            await update_user(partner_id, ban_until=ban_time.isoformat())
            try:
                await callback.bot.send_message(partner_id, "🛑 На тебя поступили повторные жалобы за скам. Бан на 1 час.")
            except: pass
        # Potentially reset count or keep going? 
        # User said "6 жаб (второй цикл) - бан на 1 час". 
        # I'll keep it simple for now.

    await callback.answer()
