from typing import Callable, Awaitable, Dict, Any, List

from plugins.db_manager.uow import UnitOfWork
from plugins.skip_updates import MessagesUpdateSkipper

from aiogram import BaseMiddleware
from aiogram.types import Message

from plugins.telegram_info_collect.factories.chat_member import ChatMemberServiceFactory

from ..factories.call import CallPluginChatMemberUnregServiceFactory

class CallMiddleware(BaseMiddleware):
    def __init__(
        self,
        message_skipper: MessagesUpdateSkipper,
        users_tag_per_line: int,
        emojies: List[str],
        default_call_message: str,
        call_footer: str = "",
    ):
        self.message_skipper = message_skipper
        self.users_tag_per_line = users_tag_per_line
        self.emojies = emojies
        self.default_call_message = default_call_message
        self.call_footer = call_footer

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["uow_factory"] = data.get("db_manager:uow_factory")

        data["users_tag_per_line"] = self.users_tag_per_line
        data["emojies"] = self.emojies
        data["default_call_message"] = self.default_call_message
        data["call_footer"] = self.call_footer

        if self.message_skipper.should_skip(message):
            return

        uow_factory: Callable[[], UnitOfWork] = data.get("db_manager:uow_factory")

        async with uow_factory() as uow:
            chat_member_service = ChatMemberServiceFactory(uow.session).create()
            chat_member = await chat_member_service.get_by_user_and_chat_tg_ids(
                user_tg_id=message.from_user.id,
                chat_tg_id=message.chat.id
            )
            chat_member_unreg_service = CallPluginChatMemberUnregServiceFactory(uow.session).create()

            if chat_member:
                await chat_member_unreg_service.remove(chat_member.id)
            else:
                print("WARNING: CallMiddleware: chat_member not found")

        # Обработка сообщения
        result = await handler(message, data)

        return result