import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Sozlamalar
BOT_TOKEN = "9191242803:AAH6HGubwNSUzNY2hc0x2EUllen3_tFlkE4"
ADMIN_ID = 123456789  # O'zingizning Telegram ID raqamingizni yozing

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Foydalanuvchi holatlari (FSM)
class Registration(StatesGroup):
    full_name = State()
    phone = State()
    course = State()

# Yangilangan kurslar tugmalari
courses_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🐍 Python dasturlash"), KeyboardButton(text="🌐 Web dasturlash")],
        [KeyboardButton(text="🤖 Robototexnika"), KeyboardButton(text="🔒 Kiberxavfsizlik")],
        [KeyboardButton(text="📐 Matematika"), KeyboardButton(text="🇰🇷 Koreys tili")],
        [KeyboardButton(text="🎨 Grafik dizayn"), KeyboardButton(text="🇬🇧 Ingliz tili")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# 1. /start buyrug'i
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! O‘quv markazimiz botiga xush kelibsiz.\n"
        "Kursga yozilish uchun iltimos, **ism va familiyangizni** kiriting:",
        parse_Mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.full_name)

# 2. Ism-familiyani qabul qilish
@dp.message(Registration.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        "Rahmat! Endi **telefon raqamingizni** yuboring (pastdagi tugmani bosing yoki +998... shaklida yozing):",
        parse_mode="Markdown",
        reply_markup=phone_kb
    )
    await state.set_state(Registration.phone)

# 3. Telefon raqamni qabul qilish
@dp.message(Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)
    await message.answer(
        "Qaysi **kursga** yozilmoqchisiz? Quyidagilardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=courses_kb
    )
    await state.set_state(Registration.course)

# 4. Kursni qabul qilish va ma'lumotlarni adminga yuborish
@dp.message(Registration.course)
async def process_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    data = await state.get_data()

    # Foydalanuvchiga tasdiqlash xabari
    user_text = (
        "✅ **Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!**\n\n"
        f"👤 **Ism-familiya:** {data['full_name']}\n"
        f"📞 **Telefon:** {data['phone']}\n"
        f"📚 **Tanlangan kurs:** {data['course']}\n\n"
        "Tez orada menejerlarimiz siz bilan bog‘lanishadi. Qayta yozilish uchun /start bosing."
    )
    await message.answer(user_text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

    # Adminga yangi ariza haqida xabar yuborish
    admin_text = (
        "🆕 **Yangi o‘quvchi ro‘yxatdan o‘tdi!**\n\n"
        f"👤 **Ism:** {data['full_name']}\n"
        f"📞 **Tel:** {data['phone']}\n"
        f"📚 **Kurs:** {data['course']}\n"
        f"🔗 **Telegram:** @{message.from_user.username or 'Mavjud emas'} (ID: `{message.from_user.id}`)"
    )
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Adminga xabar yuborishda xatolik: {e}")

    await state.clear()

# Botni ishga tushirish
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
