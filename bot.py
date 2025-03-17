import enum

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

@bot.on_message(filters.private)
async def get_user_name(client, message):
    confirmation_message = await message.reply(
        text=f"Nice to meet you! Is {message.text} you correct name?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yes",
                        callback_data=f"{ActionCategory.CONFIRM_NAME.value}:{ConfirmNameAction.CONFIRM.value}"
                    ),
                    InlineKeyboardButton(
                        text="No",
                        callback_data=f"{ActionCategory.CONFIRM_NAME.value}:{ConfirmNameAction.REJECT.value}"
                    ),
                ],
            ],
        ),
    )

    confirmation_message.custom_data = {"name": message.text}

async def handle_user_name_confirmation(client, callback_query, action):

    if action == ConfirmNameAction.CONFIRM.value:
        name = callback_query.message.custom_data["name"]
        callback_query.message.edit_message(f"Great! I'll remember you as {name}")
        print(f"User with id '{callback_query.from_user.id}' and name '{name}' is saved to database")
    elif action == ConfirmNameAction.REJECT.value:
        await callback_query.message.edit_text(
            "No worries! Please tell me your correct name."
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
        category, action = data.split(":", 1)
    except ValueError:
        await callback_query.message.reply_text("Invalid callback!")
        return

    handler = ACTION_CATEGORIES_MAP.get(category)
    if handler:
        await handler(client, callback_query, action)
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