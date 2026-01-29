from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberOwner,
    ChatMemberRestricted,
    ChatMember,
    ChatMemberBanned
)

async def is_banned_rights(tg_chat_member) -> bool:
    if isinstance(tg_chat_member, ChatMemberBanned):
        return True

async def is_standard_member_rights(tg_chat_member) -> bool:
    if isinstance(tg_chat_member, ChatMember):
        return True

async def is_restricted_rights(tg_chat_member) -> bool:
    if isinstance(tg_chat_member, ChatMemberRestricted):
        return True

async def is_admin(tg_chat_member) -> bool:
    if isinstance(tg_chat_member, ChatMemberAdministrator) or isinstance(tg_chat_member, ChatMemberOwner):
        return True

async def is_super_admin_rights(tg_chat_member) -> bool:
    if isinstance(tg_chat_member, ChatMemberAdministrator):
        if tg_chat_member.can_promote_members:
            return True
        return False
    if isinstance(tg_chat_member, ChatMemberOwner):
        return True
    return False

async def is_owner(tg_chat_member) -> bool:
    if isinstance(tg_chat_member, ChatMemberOwner):
        return True