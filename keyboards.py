from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb():
    kb = [
        [KeyboardButton(text="🐻 Выбрать берлогу")],
        [KeyboardButton(text="⚡️ Быстрый поиск")],
        [KeyboardButton(text="👤 Мой профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_gender_kb(mode: str = "set"):
    kb = [
        [InlineKeyboardButton(text="🧔 Мужской", callback_data=f"{mode}_gender_M")],
        [InlineKeyboardButton(text="👩 Женский", callback_data=f"{mode}_gender_F")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_target_gender_kb(mode: str = "set"):
    kb = [
        [InlineKeyboardButton(text="🧔 Мужчин", callback_data=f"{mode}_target_M")],
        [InlineKeyboardButton(text="👩 Женщин", callback_data=f"{mode}_target_F")],
        [InlineKeyboardButton(text="🐾 Всех", callback_data=f"{mode}_target_Any")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_categories_kb(selected_categories: list):
    categories = {
        "IT-берлога": "💻",
        "Ночной лес (18+)": "🌙",
        "Игровая пещера": "🎮",
        "Подслушано в лесу": "👂",
        "Биржа охотников": "💼",
        "Зона дзен": "🧘"
    }
    
    buttons = []
    keys = list(categories.keys())
    # Create 2 columns
    for i in range(0, len(keys), 2):
        row = []
        for j in range(2):
            if i + j < len(keys):
                cat = keys[i+j]
                icon = categories[cat]
                is_selected = cat in selected_categories
                status = "🟢" if is_selected else "🔘"
                row.append(InlineKeyboardButton(
                    text=f"{status} {icon} {cat}", 
                    callback_data=f"toggle_cat_{cat}"
                ))
        buttons.append(row)
    
    if selected_categories:
        buttons.append([InlineKeyboardButton(text="🔥 НАЧАТЬ ПОИСК", callback_data="start_search_multi")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_chat_kb():
    kb = [
        [KeyboardButton(text="🔄 Следующий"), KeyboardButton(text="👤 Поделиться профилем")],
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
        [InlineKeyboardButton(text="📝 Изменить возраст", callback_data="edit_age")],
        [InlineKeyboardButton(text="🎭 Изменить пол", callback_data="edit_gender")],
        [InlineKeyboardButton(text="🔍 Кого ищем?", callback_data="edit_target")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_rating_kb(partner_id: int):
    kb = [
        [InlineKeyboardButton(text="👍 Хорошо", callback_data=f"rate_good_{partner_id}"), 
         InlineKeyboardButton(text="👎 Плохо", callback_data=f"rate_bad_{partner_id}")],
        [InlineKeyboardButton(text="🚨 Скам", callback_data=f"rate_scam_{partner_id}"), 
         InlineKeyboardButton(text="📺 Реклама", callback_data=f"rate_ad_{partner_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
