from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from settings import settings

bot: Client = Client(
    name="NutriBot",
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.BOT_TOKEN,
)


menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Option1"),
            KeyboardButton("Option2"),
            KeyboardButton("Option3")
        ]
    ],
    resize_keyboard=True,
)

@bot.on_message(filters.command("start"))
async def echo(client, message):
    await message.reply("Chose option", reply_markup=menu)

bot.run()