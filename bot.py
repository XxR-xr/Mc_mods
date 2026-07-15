import sqlite3
import json
from aiogram import Bot, Dispatcher, types, executor

# ⚠️ O'z ma'lumotlaringizni yozing (hech qanday proxy shart emas!)
BOT_TOKEN = "8863751780:AAERMNLkm4kddjEwZdn2YxkPokDKjO-ZzFo" 
ADMIN_ID = 7667103099  # Telegram ID raqamingiz

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
DATABASE = 'database.db'  # Koyeb uchun bazani shu yerga o'zgartirdik

user_temp_data = {}

# 1. Mini App orqali yuklab olishni qabul qilish
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def web_app_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "get_mod":
            file_id = data.get("file_id")
            await message.answer("Siz tanlagan mod yuborilmoqda, kuting...")
            await bot.send_document(message.chat.id, file_id)
    except Exception as e:
        await message.answer(f"Faylni yuborishda xatolik: {e}")

# 2. Start buyrug'i
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(url="https://XxR-xr.github.io/Mc_mods/")
    markup.add(types.KeyboardButton(text="Modlar Do'koni 🎮", web_app=web_app))
    await message.answer("Minecraft Modlar do'koniga xush kelibsiz! Saytni ochish uchun pastdagi tugmani bosing.", reply_markup=markup)

# 3. Admin uchun mod qo'shish
@dp.message_handler(commands=['addmod'])
async def add_mod(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Yangi mod qo'shish uchun quyidagi ko'rinishda yozing:\n\n"
        "Nomi | Versiyasi | Platforma (java yoki bedrock) | Tavsifi"
    )

# 4. Mod matnli ma'lumotlarini qabul qilish
@dp.message_handler(lambda message: '|' in message.text)
async def process_mod_text(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = [p.strip() for p in message.text.split('|')]
        if len(parts) < 4:
            await message.answer("Xato format. Ma'lumotlarni to'liq kiriting.")
            return
        
        user_temp_data[message.from_user.id] = {
            'title': parts[0],
            'version': parts[1],
            'platform': parts[2].lower(),
            'description': parts[3]
        }
        await message.answer("Tafsilotlar saqlandi. Endi mod faylini (.jar yoki .mcpack) Document ko'rinishida yuboring.")
    except Exception as e:
        await message.answer(f"Xatolik: {e}")

# 5. Mod faylini qabul qilib bazaga saqlash
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def process_mod_file(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        await message.answer("Avval `/addmod` yordamida matnli ma'lumotlarni yuboring.")
        return

    mod_info = user_temp_data[user_id]
    file_id = message.document.file_id

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        "INSERT INTO mods (title, version, platform, description, file_id) VALUES (?, ?, ?, ?, ?)",
        (mod_info['title'], mod_info['version'], mod_info['platform'], mod_info['description'], file_id)
    )
    conn.commit()
    conn.close()

    del user_temp_data[user_id]
    await message.answer(f"🎉 '{mod_info['title']}' modi muvaffaqiyatli saqlandi!")

if __name__ == '__main__':
    # Bazani avtomatik yaratish
    conn = sqlite3.connect(DATABASE)
    conn.execute('''CREATE TABLE IF NOT EXISTS mods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        version TEXT NOT NULL,
        platform TEXT NOT NULL,
        description TEXT,
        file_id TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
    
    executor.start_polling(dp, skip_updates=True)
      
