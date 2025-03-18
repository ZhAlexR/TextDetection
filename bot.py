import enum

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from mongo_client import bot_mongo_client
from settings import settings
from textract import get_nutrition_table

bot: Client = Client(
    name="NutriBot",
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.BOT_TOKEN,
)

class ActionCategory(enum.Enum):
    CONFIRM_NAME = "confirm_name"

class ConfirmNameAction(enum.Enum):
    CONFIRM = "confirm"
    REJECT = "reject"

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "Hi! I am NutriBot. My main goal is to assist you with calories counting process, "
        "but first tell me your name."
    )

@bot.on_message(filters.private & filters.text)
async def get_user_name(client, message):
    await message.reply(
        text=f"Nice to meet you! Is <b>{message.text}</b> you correct name?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yes",
                        callback_data=f"{ActionCategory.CONFIRM_NAME.value}:{ConfirmNameAction.CONFIRM.value}:{message.text}"
                    ),
                    InlineKeyboardButton(
                        text="No",
                        callback_data=f"{ActionCategory.CONFIRM_NAME.value}:{ConfirmNameAction.REJECT.value}"
                    ),
                ],
            ],
        ),
        parse_mode=enums.ParseMode.HTML,
    )


async def handle_user_name_confirmation(client, callback_query, action, *args):
    if action == ConfirmNameAction.CONFIRM.value:
        name = args[0]
        await callback_query.message.edit_text(f"Great! I'll remember you as <b>{name}</b>", parse_mode=enums.ParseMode.HTML)
        bot_mongo_client.users.insert_one({
            "telegram_user_id": callback_query.from_user.id,
            "user_name": name
        })
    elif action == ConfirmNameAction.REJECT.value:
        await callback_query.message.edit_text(
            "No worries! Please tell me your correct name.",
            parse_mode=enums.ParseMode.HTML
        )


ACTION_CATEGORIES_MAP = {
    ActionCategory.CONFIRM_NAME.value: handle_user_name_confirmation
}

@bot.on_callback_query()
async def handle_callback(client: Client, callback_query):
    data = callback_query.data
    if not data:
        return

    try:
        category, action, *args = data.split(":")
    except ValueError:
        await callback_query.message.reply_text("Invalid callback!")
        return

    handler = ACTION_CATEGORIES_MAP.get(category)
    if handler:
        await handler(client, callback_query, action, *args)
    else:
        await callback_query.message.reply_text("Unknown action!")


@bot.on_message(filters.photo)
async def handle_photo(client, message):
    file = await client.download_media(message.photo.file_id, in_memory=True)
    await message.reply("Extracting nutrition table ...")
    byte_file = bytes(file.getbuffer())
    nutrition = get_nutrition_table(byte_file)
    await message.reply(nutrition.__str__())

bot.run()
