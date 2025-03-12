from pyrogram import Client, filters

from settings import settings

bot_client: Client = Client(
    name="NutriBot",
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.BOT_TOKEN,
)

@bot_client.on_message(filters.text & filters.private)
async def echo(client, message):
    await message.reply(message.text)


bot_client.run()