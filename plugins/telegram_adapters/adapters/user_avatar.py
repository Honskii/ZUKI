import io
from typing import Optional
from PIL import Image
from aiogram import Bot
from aiogram.types import Message

async def fetch_last_avatar(user_id: int, bot: Bot) -> Optional[bytes]:
    avatar_bytes = None
    try:
        user_profile_photos = await bot.get_user_profile_photos(user_id)
        if user_profile_photos.total_count > 0:
            # Берем самую большую версию последней аватарки
            photo_file_id = user_profile_photos.photos[0][-1].file_id
            file_info = await bot.get_file(photo_file_id)

            # Скачиваем в память
            avatar_io = io.BytesIO()
            await bot.download_file(file_info.file_path, avatar_io)
            avatar_bytes = avatar_io.getvalue()
        else:
            with Image.open("src/img/photo_img_default.png") as img:
                b_io = io.BytesIO()
                img.save(b_io, format="PNG")
                avatar_bytes = b_io.getvalue()
    except Exception as e:
        print(f"Ошибка при получении аватарки: {e}")
        pass

    return avatar_bytes