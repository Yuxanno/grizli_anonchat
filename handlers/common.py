import os
from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import get_user, create_user, update_user
from keyboards import get_main_menu_kb, get_categories_kb, get_profile_kb

router = Router()

LOGO_PATH = "logo.png"

class RegistrationStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_new_age = State()

CATEGORY_DESCRIPTIONS = (
    "🐻 **Выбирай свою берлогу:**\n\n"
    "💻 **✅ IT-берлога**: Обсуждай код, серверы и девайсы без лишних глаз.\n"
    "🌙 **✅ Ночной лес (18+)**: Анонимный флирт и знакомства. Мы уважаем приватность.\n"
    "🎮 **✅ Игровая пещера**: Ищи тимейтов, обсуждай катки без токсичности.\n"
    "👂 **✅ Подслушано в лесу**: Анонимные истории, сплетни и признания.\n"
    "💼 **✅ Биржа охотников**: Честные разговоры о работе и зарплатах.\n"
    "🧘 **✅ Зона дзен**: Глубокие разговоры о жизни и психологии."
)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        user = await create_user(message.from_user.id)
    
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
    
    await message.answer(
        "Теперь ты один из нас. Выбирай категорию и начинай рычать! 🛡",
        reply_markup=get_main_menu_kb()
    )

@router.message(F.text == "🐻 Выбрать берлогу")
@router.message(F.text == "🔙 Назад")
async def cmd_choose_den(message: Message):
    user = await get_user(message.from_user.id)
    if not user or user.get("age") is None:
        return await message.answer("Сначала скажи, сколько тебе зим! 🐻")
    
    await message.answer(CATEGORY_DESCRIPTIONS, reply_markup=get_categories_kb(), parse_mode="Markdown")

@router.message(F.text == "👤 Мой профиль")
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user: return
    
    profile_text = (
        f"👤 **Твой профиль:**\n"
        f"🐻 Возраст: {user.get('age', 'Не указан')}\n"
        f"🎭 Статус: {user.get('status', 'idle')}\n"
        f"📍 Категория: {user.get('category', 'Нет')}\n"
        f"💾 Сохраненная категория: {user.get('last_category', 'Нет')}"
    )
    await message.answer(profile_text, reply_markup=get_profile_kb(), parse_mode="Markdown")

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
            try:
                await message.bot.send_message(partner_id, "Собеседник покинул берлогу... 🐻", reply_markup=get_main_menu_kb())
            except Exception:
                pass
        
        await update_user(message.from_user.id, status="idle", category=None, partner_id=None)
        await message.answer("Возвращаемся на опушку. 🐻", reply_markup=get_main_menu_kb())
