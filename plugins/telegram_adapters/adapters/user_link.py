from aiogram import Bot
from aiogram.types import Message

async def get_user_link(chat_id: int, user_id: int, bot: Bot) -> str:
    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)
        name = chat_member.user.full_name
        username = chat_member.user.username
        if username:
            return f"<a href='t.me/{username}'>{name}</a>"
        else:
            return f"<a href='tg://openmessage?id={user_id}'>{name}</a>"
    except Exception as e:
        print("Error fetching chat member:", e)
        return f"<a href='tg://openmessage?id={user_id}'>{user_id}</a>"