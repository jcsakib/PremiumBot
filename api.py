import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GROUPS = [os.getenv("GROUP1"), os.getenv("GROUP2"), os.getenv("GROUP3")]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

DATA_FILE = "db.json"

# Helper Functions
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def check_joined(user_id):
    for group in GROUPS:
        try:
            member = await bot.get_chat_member(chat_id=group, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# Start Command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = """💰 প্রতিদিন 30-40 হাজার টাকা ইনকাম করতে চান? 😱
--------------------------------------------
🔥 এখন আর লস নিয়ে চিন্তা করতে হবে না!
কারণ এখানে পাচ্ছেন 100% LOSS RECOVERY GUARANTEE 💯

✅ ভেরিফাই করার ধাপ:
1️⃣ নিচের ৩টি চ্যানেলে অবশ্যই জয়েন করুন
2️⃣ সবগুলো জয়েন করার পর "✅ Verify" বাটনে ক্লিক করুন
--------------------------------------------"""
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("GROUP 1", url="https://t.me/tigro_signal"),
        InlineKeyboardButton("GROUP 2", url="https://t.me/free_online_income_tigro"),
        InlineKeyboardButton("GROUP 3", url="https://t.me/LIVE_Crash_Hack_Signal"),
        InlineKeyboardButton("✅ Verify", callback_data="verify")
    )
    await message.answer(text, reply_markup=keyboard)

# Verify Callback
@dp.callback_query_handler(lambda c: c.data=="verify")
async def verify_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    joined = await check_joined(user_id)
    
    if joined:
        data = load_data()
        data[str(user_id)] = {"status":"pending"}
        save_data(data)
        
        premium_text = """🎯 Premium Signal Instructions:
1️⃣ Open Account: https://www.tigroclub.net/#/register?invitationCode=57755110895
2️⃣ Add Payment Method
3️⃣ Deposit minimum 500 Tk
4️⃣ Send Screenshot + Tigro ID to Admin
5️⃣ Admin Approves → Verified ✅
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✅ Send to Admin", callback_data="send_admin"))
        await bot.send_message(chat_id=user_id, text=premium_text, reply_markup=keyboard)
        
        try:
            await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        except:
            pass
    else:
        await bot.answer_callback_query(callback.id, "❌ সব গ্রুপে Join করেননি।")

# Send to Admin
@dp.callback_query_handler(lambda c: c.data=="send_admin")
async def send_admin(callback: types.CallbackQuery):
    user = callback.from_user
    await bot.send_message(ADMIN_ID, f"User @{user.username} ({user.id}) wants verification.")
    await bot.answer_callback_query(callback.id, "✅ Request sent to Admin.")

# Flask Webhook
@app.route("/api", methods=["POST"])
def webhook():
    try:
        update = types.Update(**request.json)
        asyncio.run(dp.process_update(update))
    except Exception as e:
        print(f"Error: {e}")
    return "ok"

# Health Check
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"
