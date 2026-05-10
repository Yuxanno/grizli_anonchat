import os
from datetime import datetime
from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import get_user, create_user, update_user
from keyboards import get_main_menu_kb, get_categories_kb, get_profile_kb

router = Router()

LOGO_PATH = "logo.png"

CATEGORY_DESCRIPTIONS = (
    "🏰 **ДОСТУПНЫЕ БЕРЛОГИ:**\n\n"
    "💻 **IT-берлога**: Обсуждай код, серверы и девайсы.\n"
    "🌙 **Ночной лес (18+)**: Анонимный флирт и знакомства.\n"
    "🎮 **Игровая пещера**: Ищи тимейтов и обсуждай катки.\n"
    "👂 **Подслушано в лесу**: Истории, сплетни и признания.\n"
    "💼 **Биржа охотников**: О работе и зарплатах.\n"
    "🧘 **Зона дзен**: Психология и разговоры о жизни."
)

class RegistrationStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_new_age = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        user = await create_user(message.from_user.id)
    
    # Ban check
    if user.get("ban_until"):
        ban_until = datetime.fromisoformat(user["ban_until"])
        if ban_until > datetime.now():
            remaining = ban_until - datetime.now()
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            return await message.answer(f"🛑 Ты временно изгнан из леса. \nОсталось: {mins} мин. {secs} сек. 🐻")

    greeting = (
        "🐻 Привет! Добро пожаловать в **Anon Griz Chat**. 🎭\n\n"
        "Здесь ты можешь найти собеседника в разных берлогах и пообщаться анонимно. 🛡"
    )
    
    if os.path.exists(LOGO_PATH):
        await message.answer_photo(
            FSInputFile(LOGO_PATH),
            caption=greeting,
            parse_mode="Markdown"
        )
    else:
        await message.answer(greeting, parse_mode="Markdown")

    if user.get("age") is None:
        await message.answer("Прежде чем пущу в лес — сколько тебе лет? Введи только цифру. 🐻")
        await state.set_state(RegistrationStates.waiting_for_age)
    elif user.get("gender") is None:
        from keyboards import get_gender_kb
        await message.answer("Укажи свой пол: 🛡", reply_markup=get_gender_kb())
    else:
        await message.answer(
            "Выбирай берлогу, охотник! 🛡",
            reply_markup=get_main_menu_kb()
        )

@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer("Рычи четче! Введи возраст только цифрами. 🐻")
    
    age = int(message.text)
    if age < 5 or age > 100:
        return await message.answer("Такие звери в нашем лесу не водятся. Введи реальный возраст! 🐻")

    await update_user(message.from_user.id, age=age)
    await state.clear()
    
    from keyboards import get_gender_kb
    await message.answer(f"Принято! Тебе {age}. Теперь укажи свой пол: 🛡", reply_markup=get_gender_kb())

@router.callback_query(F.data.startswith("set_gender_"))
async def process_set_gender(callback: types.CallbackQuery):
    gender = callback.data.split("_")[-1]
    await update_user(callback.from_user.id, gender=gender)
    
    from keyboards import get_target_gender_kb
    await callback.message.edit_text("Отлично! А кого ты ищешь в этом лесу? 🐾", reply_markup=get_target_gender_kb())
    await callback.answer()

@router.callback_query(F.data.startswith("set_target_"))
async def process_set_target(callback: types.CallbackQuery):
    target = callback.data.split("_")[-1]
    await update_user(callback.from_user.id, target_gender=target)
    
    await callback.message.delete()
    await callback.message.answer(
        "Все готово! Выбирай берлогу и начинай охоту. 🛡",
        reply_markup=get_main_menu_kb()
    )
    await callback.answer()

@router.message(F.text == "🐻 Выбрать берлогу")
@router.message(F.text == "🔙 Назад")
async def cmd_choose_den(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user.get("age") is None:
        return await message.answer("Сначала скажи, сколько тебе зим! 🐻")
    
    from keyboards import get_categories_kb
    selected = user.get("selected_categories", [])
    await message.answer(
        CATEGORY_DESCRIPTIONS + "\n\n*Выбери одну или несколько берлог:*", 
        reply_markup=get_categories_kb(selected), 
        parse_mode="Markdown"
    )

@router.message(F.text == "👤 Мой профиль")
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user: return
    
    gender_map = {"M": "🧔 Мужской", "F": "👩 Женский", None: "Не указан"}
    target_map = {"M": "🧔 Мужчин", "F": "👩 Женщин", "Any": "🐾 Всех"}
    
    selected = user.get("selected_categories", [])
    if len(selected) > 3:
        cats_str = f"{len(selected)} берлог"
    else:
        cats_str = ", ".join(selected) or "Не выбраны"
    
    profile_text = (
        f"👤 **ТВОЙ ПРОФИЛЬ:**\n\n"
        f"🎂 **Возраст:** {user.get('age', '—')}\n"
        f"🎭 **Пол:** {gender_map.get(user.get('gender'))}\n"
        f"🔍 **Ищу:** {target_map.get(user.get('target_gender', 'Any'))}\n"
        f"📍 **Берлоги:** {cats_str}\n"
        f"💾 **Статус:** `{user.get('status', 'idle')}`"
    )
    await message.answer(profile_text, reply_markup=get_profile_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "edit_gender")
async def process_edit_gender(callback: types.CallbackQuery):
    from keyboards import get_gender_kb
    await callback.message.answer("Выбери свой пол: 🛡", reply_markup=get_gender_kb(mode="update"))
    await callback.answer()

@router.callback_query(F.data == "edit_target")
async def process_edit_target(callback: types.CallbackQuery):
    from keyboards import get_target_gender_kb
    await callback.message.answer("Кого ты хочешь найти? 🐾", reply_markup=get_target_gender_kb(mode="update"))
    await callback.answer()

@router.callback_query(F.data.startswith("update_gender_"))
async def process_update_gender(callback: types.CallbackQuery):
    gender = callback.data.split("_")[-1]
    await update_user(callback.from_user.id, gender=gender)
    await callback.message.edit_text("✅ Твой пол успешно обновлен!")
    await callback.answer()

@router.callback_query(F.data.startswith("update_target_"))
async def process_update_target(callback: types.CallbackQuery):
    target = callback.data.split("_")[-1]
    await update_user(callback.from_user.id, target_gender=target)
    await callback.message.edit_text("✅ Твои предпочтения обновлены!")
    await callback.answer()

@router.callback_query(F.data == "edit_age")
async def process_edit_age_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Сколько тебе зим на самом деле? Введи только цифру. 🐻")
    await state.set_state(RegistrationStates.waiting_for_new_age)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_new_age)
async def process_new_age(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer("Рычи четче! Введи возраст только цифрами. 🐻")
    
    age = int(message.text)
    if age < 5 or age > 100:
        return await message.answer("Такие звери в нашем лесу не водятся. Введи реальный возраст! 🐻")

    await update_user(message.from_user.id, age=age)
    await state.clear()
    
    await message.answer(
        f"Данные обновлены! Теперь тебе {age}. 🛡",
        reply_markup=get_main_menu_kb()
    )

@router.message(F.text == "Отменить поиск")
@router.message(F.text == "🔙 Выход в меню")
async def cmd_stop_search(message: Message):
    user = await get_user(message.from_user.id)
    if user:
        from database import end_chat
        partner_id = await end_chat(message.from_user.id)
        if partner_id:
            from keyboards import get_rating_kb
            try:
                await message.bot.send_message(partner_id, "Собеседник покинул берлогу... Оцени его: 🐻", reply_markup=get_rating_kb(message.from_user.id))
            except Exception:
                pass
        
        await update_user(message.from_user.id, status="idle", category=None, partner_id=None)
        await message.answer("Возвращаемся на опушку. 🐻", reply_markup=get_main_menu_kb())
