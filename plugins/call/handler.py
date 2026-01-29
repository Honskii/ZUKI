import math
import re
from typing import List

from aiogram import F
from aiogram.filters import Command, or_f
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner

from plugins.db_manager import UnitOfWork
from plugins.telegram_info_collect.factories.chat_member import ChatMemberServiceFactory
from plugins.telegram_info_collect.factories.chat import ChatServiceFactory
from plugins.telegram_adapters.adapters.user_link import (get_user_link_with_notification)
from plugins.telegram_adapters.adapters.member_rights import is_super_admin_rights

from .router import router
from .domains.call import CallDomain
from .factories.call import (
    CallPluginChatEnabledServiceFactory,
    CallPluginChatMemberUnregServiceFactory
)

@router.message(F.text.regexp(r"(?is)^калл(.+)?$"), F.chat.type.in_({"group", "supergroup"}))
async def call_handler(
    message: Message,
    uow_factory: UnitOfWork,
    users_tag_per_line: int,
    emojies: List[str],
    default_call_message: str,
    call_footer: str = "",
):

    chat_tg_id = message.chat.id
    user_tg_id = message.from_user.id

    tg_chat_member = await message.bot.get_chat_member(
        chat_id=chat_tg_id,
        user_id=user_tg_id
    )

    if not await is_super_admin_rights(tg_chat_member):
        return None

    call_message = ""
    matches = re.match(r"(?is)^калл(.+)$", message.text)
    if not matches is None:
        call_message = matches.group(1).strip()

    first_message = call_message or default_call_message.format(full_name=message.from_user.full_name)
    last_message = call_message + call_footer.format(full_name=message.from_user.full_name)

    # Check if call is enabled in chat
    async with uow_factory() as uow:
        chat_service = ChatServiceFactory(uow.session).create()
        chat = await chat_service.get_by_tg_id(chat_tg_id)
        if chat is None:
            print(f"WARNING: Chat not found during call: {chat_tg_id=}")
            return None

        chat_enabled_service = CallPluginChatEnabledServiceFactory(uow.session).create()
        chat_enabled_obj = await chat_enabled_service.get_by_chat_id(chat.id)
        if chat_enabled_obj is None:
            return None
        is_enabled = await chat_enabled_service.check(chat_enabled_obj.id)
        if is_enabled is None:
            return None

    is_preview_disabled = False
    if message.link_preview_options and message.link_preview_options.is_disabled == True:
        is_preview_disabled = True

    # Send call messages
    async with uow_factory() as uow:
        chat_member_service = ChatMemberServiceFactory(uow.session).create()
        unreg_service = CallPluginChatMemberUnregServiceFactory(uow.session).create()

        chat_members = await unreg_service.list_not_unreg_by_chat_ids(
            [chat.id],
            statuses = [
                "administrator",
                "creator",
                "member",
                "restricted"
            ]
        )

        if not chat_members:
            return None

        number_of_messages = math.ceil(len(chat_members) / users_tag_per_line)

        for i in range(number_of_messages):
            several_chat_members = chat_members[users_tag_per_line*i:users_tag_per_line*(i+1)]
            chat_member_links = []
            for chat_member in several_chat_members:
                user = await chat_member_service.get_user(chat_member)
                user_link = await get_user_link_with_notification(
                    user_id=user.tg_id,
                    call_sign=CallDomain.get_user_emoji(
                        user.first_name + (user.last_name or ""),
                        call_signs=emojies
                    )
                )
                chat_member_links.append(user_link)

            current_call_message = call_message
            if i == 0:
                current_call_message = first_message
            elif i == number_of_messages - 1:
                current_call_message =  last_message

            await message.answer(
                f"{current_call_message}\n\n{' '.join(chat_member_links)}",
                disable_web_page_preview=is_preview_disabled,
                parse_mode="HTML"
            )

@router.message(
    or_f(
        F.text.regexp(r"(?i)^анрег$"),
        Command("unreg")
    ),
    F.chat.type.in_({"group", "supergroup"})
)
async def call_unreg_handler(message: Message, uow_factory: UnitOfWork):
    chat_tg_id = message.chat.id
    user_tg_id = message.from_user.id

    async with uow_factory() as uow:
        chat_member_service = ChatMemberServiceFactory(uow.session).create()
        chat_member = await chat_member_service.get_by_user_and_chat_tg_ids(
            chat_tg_id=chat_tg_id,
            user_tg_id=user_tg_id
        )
        if chat_member is None:
            print("WARNING: Chat member not found during unreg")
            return None
        chat_member_unreg_service = CallPluginChatMemberUnregServiceFactory(uow.session).create()
        await chat_member_unreg_service.add(chat_member.id)
    await message.reply("📝 На период неаткивности вы будете исключены из общего призыва", parse_mode="HTML")

@router.message(
    or_f(
        F.text.regexp(r"(?i)^\+каллы?$"),
        Command("call_enable")
    ),
    F.chat.type.in_({"group", "supergroup"})
)
async def call_enable_handler(message: Message, uow_factory: UnitOfWork):
    chat_tg_id = message.chat.id

    tg_chat_member = await message.bot.get_chat_member(
        chat_id=chat_tg_id,
        user_id=message.from_user.id
    )

    if not await is_super_admin_rights(tg_chat_member):
        return None

    async with uow_factory() as uow:
        chat_service = ChatServiceFactory(uow.session).create()
        chat = await chat_service.get_by_tg_id(chat_tg_id)
        if chat is None:
            print(f"WARNING: Chat not found during call enable: {chat_tg_id=}")
            return None

        call_plugin_chat_enabled_service = CallPluginChatEnabledServiceFactory(uow.session).create()
        await call_plugin_chat_enabled_service.add(chat.id)

    await message.answer("✅ Калл успешно <b>включён</b> в этом чате!", parse_mode="HTML")

@router.message(
    or_f(
        F.text.regexp(r"(?i)^\-каллы?$"),
        Command("call_disable")
    ),
    F.chat.type.in_({"group", "supergroup"})
)
async def call_disable_handler(message: Message, uow_factory: UnitOfWork):
    chat_tg_id = message.chat.id

    tg_chat_member = await message.bot.get_chat_member(
        chat_id=chat_tg_id,
        user_id=message.from_user.id
    )

    if not await is_super_admin_rights(tg_chat_member):
        return None

    async with uow_factory() as uow:
        chat_service = ChatServiceFactory(uow.session).create()
        chat = await chat_service.get_by_tg_id(chat_tg_id)
        if chat is None:
            print(f"WARNING: Chat not found during call disable: {chat_tg_id=}")
            return None

        chat_enabled_service = CallPluginChatEnabledServiceFactory(uow.session).create()
        call_enable_obj = await chat_enabled_service.get_by_chat_id(chat.id)
        if call_enable_obj:
            await chat_enabled_service.delete(call_enable_obj)

    await message.answer("✅ Калл успешно <b>отключён</b> в этом чате!", parse_mode="HTML")