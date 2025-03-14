from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from settings import settings
from textract import get_nutrition_table

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
async def start(client, message):
    await message.reply("Chose option", reply_markup=menu)


@bot.on_message(filters.photo)
async def handle_photo(client, message):
    file = await client.download_media(message.photo.file_id, in_memory=True)
    await message.reply("Extracting nutrition table ...")
    byte_file = bytes(file.getbuffer())
    nutrition = get_nutrition_table(byte_file)
    await message.reply(nutrition.__str__())


bot.run()