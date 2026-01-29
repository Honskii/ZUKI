from aiogram import Bot

async def get_user_link(chat_id: int, user_id: int, bot: Bot) -> str:
    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)
        name = chat_member.user.full_name
        username = chat_member.user.username
        if username:
            return f"<a href='https://t.me/{username}'>{name}</a>"
        else:
            return f"<a href='`tg://openmessage?id={user_id}'>{name}</a>"
    except Exception as e:
        print("Error fetching chat member:", e)
        return f"<a href='`tg://openmessage?id={user_id}'>{user_id}</a>"

async def get_user_link_with_notification(user_id: int, call_sign) -> str:
    return f"<a href='tg://tg?id={user_id}'>{call_sign}</a>"