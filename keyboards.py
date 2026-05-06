from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb():
    kb = [
        [KeyboardButton(text="🐻 Выбрать берлогу")],
        [KeyboardButton(text="⚡️ Быстрый поиск")],
        [KeyboardButton(text="👤 Мой профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_categories_kb():
    kb = [
        [KeyboardButton(text="✅ IT-берлога"), KeyboardButton(text="✅ Ночной лес (18+)")],
        [KeyboardButton(text="✅ Игровая пещера"), KeyboardButton(text="✅ Подслушано в лесу")],
        [KeyboardButton(text="✅ Биржа охотников"), KeyboardButton(text="✅ Зона дзен")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_chat_kb():
    kb = [
        [KeyboardButton(text="🔄 Следующий")],
        [KeyboardButton(text="🔙 Выход в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_stop_search_kb():
    kb = [
        [KeyboardButton(text="🔙 Выход в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_profile_kb():
    kb = [
        [InlineKeyboardButton(text="📝 Изменить возраст", callback_data="edit_age")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
