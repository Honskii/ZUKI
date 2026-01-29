from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.call import CallPluginChatMemberUnregModel, CallPluginChatEnabled
from plugins.telegram_info_collect.models.chat_member import ChatMember


class CallPluginChatMemberUnregRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Optional[CallPluginChatMemberUnregModel]:
        result = await self.session.execute(
            select(CallPluginChatMemberUnregModel).where(CallPluginChatMemberUnregModel.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_chat_member_id(self, chat_member_id: int) -> Optional[CallPluginChatMemberUnregModel]:
        result = await self.session.execute(
            select(CallPluginChatMemberUnregModel).where(CallPluginChatMemberUnregModel.chat_member_id == chat_member_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[CallPluginChatMemberUnregModel]:
        result = await self.session.execute(select(CallPluginChatMemberUnregModel))
        return result.scalars().all()

    async def list_unreg_by_chat_ids(self, chat_ids: List[int]) -> List[CallPluginChatMemberUnregModel]:
        """Получить всех анрегнутых участников по списку ID чатов"""
        result = await self.session.execute(
            select(CallPluginChatMemberUnregModel).join(
                ChatMember,
                CallPluginChatMemberUnregModel.chat_member_id == ChatMember.id
            ).where(ChatMember.chat_id.in_(chat_ids))
        )
        return result.scalars().all()

    async def list_not_unreg_by_chat_ids(self, chat_ids: List[int]) -> List[CallPluginChatMemberUnregModel]:
        """Получить всех неанрегнутых участников по списку ID чатов"""
        subquery = select(CallPluginChatMemberUnregModel.chat_member_id)
        result = await self.session.execute(
            select(ChatMember).where(
                ChatMember.chat_id.in_(chat_ids),
                ChatMember.id.not_in(subquery)
            )
        )
        return result.scalars().all()

    async def add(self, chat_member_id: int) -> CallPluginChatMemberUnregModel:
        obj = CallPluginChatMemberUnregModel(chat_member_id=chat_member_id)
        self.session.add(obj)
        return obj

    async def delete(self, obj: CallPluginChatMemberUnregModel) -> None:
        await self.session.delete(obj)

class CallPluginChatEnabledRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Optional[CallPluginChatEnabled]:
        result = await self.session.execute(
            select(CallPluginChatEnabled).where(CallPluginChatEnabled.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_chat_id(self, chat_id: int) -> Optional[CallPluginChatEnabled]:
        result = await self.session.execute(
            select(CallPluginChatEnabled).where(CallPluginChatEnabled.chat_id == chat_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[CallPluginChatEnabled]:
        result = await self.session.execute(select(CallPluginChatEnabled))
        return result.scalars().all()

    async def add(self, chat_id: int) -> CallPluginChatEnabled:
        obj = CallPluginChatEnabled(chat_id=chat_id)
        self.session.add(obj)
        return obj

    async def delete(self, obj: CallPluginChatEnabled) -> None:
        await self.session.delete(obj)