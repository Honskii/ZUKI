import asyncio
from datetime import datetime

from aiogram import F
from aiogram.types import Message, BufferedInputFile

from .router import router
from .service import QuoteService
from plugins.telegram_adapters.adapters.user_avatar import fetch_last_avatar

@router.message(F.text == ".цитата", F.chat.type.in_({"group", "supergroup"}))
async def quote_handler(message: Message, quote_service: QuoteService):
    if (datetime.now(tz=message.date.tzinfo) - message.date).days > 1:
        return
    if message.reply_to_message is None or message.reply_to_message.text is None:
        return

    original_msg = message.reply_to_message
    user = original_msg.from_user
    text = original_msg.text
    full_name = user.full_name
    date = original_msg.date
    avatar_bytes = await fetch_last_avatar(user.id, message.bot)
    bg_image = await quote_service.get_next_background()

    status_msg = await message.answer("🎨 Секундочку...")

    try:
        # Запуск тяжелой задачу в отдельном потоке, чтобы не блокировать бота
        loop = asyncio.get_running_loop()
        image_data = await loop.run_in_executor(
            None,
            quote_service.create_quote_image,
            bg_image, avatar_bytes, full_name, text, date
        )

        photo_file = BufferedInputFile(image_data.read(), filename="quote.jpg")
        await message.reply_photo(photo_file)
        await status_msg.delete()

    except ValueError as ve:
        await message.reply(f"Ошибка: {ve}")
        await status_msg.delete()
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        await message.reply("Произошла ошибка при создании картинки.")
        await status_msg.delete()
