from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from plugins.db_manager import UnitOfWork
from plugins.telegram_adapters.adapters.chat_mapper import TelegramChatMapper

from ..factories.chat_member import ChatMemberServiceFactory
from ..factories.user import UserServiceFactory
from ..factories.chat import ChatServiceFactory

class OuterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Update,
        data: dict,
    ) -> Any:
        sessionmaker = data["db_manager:sessionmaker"]

        if isinstance(event.event, Message):
            message: Message = event.event

            user = None
            chat = None

            async with UnitOfWork(sessionmaker) as uow:
                user_service = UserServiceFactory(uow.session).create()
                user = await user_service.put(
                    tg_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    is_bot=message.from_user.is_bot
                )

            async with UnitOfWork(sessionmaker) as uow:
                chat_service = ChatServiceFactory(uow.session).create()
                chat_type = TelegramChatMapper.to_internal_type(message.chat)

                chat = await chat_service.put(
                    tg_id=message.chat.id,
                    name=message.chat.full_name,
                    type=chat_type
                )

            async with UnitOfWork(sessionmaker) as uow:
                if user and chat:
                    tg_chat_member = await message.bot.get_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    )
                    chat_member_service = ChatMemberServiceFactory(uow.session).create()

                    role_id=None
                    if tg_chat_member.status in ["creator"]:
                        role_id=5

                    await chat_member_service.put(
                        user_tg_id=message.from_user.id,
                        chat_tg_id=message.chat.id,
                        status=tg_chat_member.status,
                        title=getattr(tg_chat_member, "custom_title", None),
                        role_id=role_id
                    )

        # Обработка сообщения
        result = await handler(event, data)

        return result
