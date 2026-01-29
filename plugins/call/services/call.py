from typing import Optional, List
from ..models.call import CallPluginChatMemberUnregModel, CallPluginChatEnabled
from ..repositories.call import (
    CallPluginChatMemberUnregRepository,
    CallPluginChatEnabledRepository,
)
from plugins.telegram_info_collect.services.chat import ChatService
from plugins.telegram_info_collect.services.chat_member import ChatMemberService


class CallPluginChatMemberUnregService:
    def __init__(
        self,
        repo: CallPluginChatMemberUnregRepository
    ):
        self.repo = repo

    async def check(self, chat_member_id: int) -> bool:
        return bool(await self.repo.get(chat_member_id))

    async def get(self, id: int) -> Optional[CallPluginChatMemberUnregModel]:
        return await self.repo.get(id)

    async def get_by_chat_member_id(self, chat_member_id: int) -> Optional[CallPluginChatMemberUnregModel]:
        return await self.repo.get_by_chat_member_id(chat_member_id)

    async def add(self, chat_member_id: int) -> CallPluginChatMemberUnregModel:
        obj = await self.get_by_chat_member_id(chat_member_id)
        if obj:
            return obj
        return await self.repo.add(chat_member_id)

    async def list(self) -> List[CallPluginChatMemberUnregModel]:
        return await self.repo.list()

    async def list_unreg_by_chat_ids(self, chat_ids: List[int]) -> List[CallPluginChatMemberUnregModel]:
        return await self.repo.list_unreg_by_chat_ids(chat_ids)

    async def list_not_unreg_by_chat_ids(self, chat_ids: List[int], statuses: List[str] = []) -> List[CallPluginChatMemberUnregModel]:
        return await self.repo.list_not_unreg_by_chat_ids(chat_ids, statuses)

    async def remove(self, chat_member_id: int) -> None:
        obj = await self.get_by_chat_member_id(chat_member_id)
        if obj:
            await self.repo.delete(obj)

    async def delete(self, obj: CallPluginChatMemberUnregModel) -> None:
        await self.repo.delete(obj)

class CallPluginChatEnabledService:
    def __init__(self, repo: CallPluginChatEnabledRepository):
        self.repo = repo

    async def check(self, id: int) -> bool:
        return bool(await self.repo.get(id))

    async def get(self, id: int) -> Optional[CallPluginChatEnabled]:
        return await self.repo.get(id)

    async def get_by_chat_id(self, chat_id: int) -> Optional[CallPluginChatEnabled]:
        return await self.repo.get_by_chat_id(chat_id)

    async def list(self) -> List[CallPluginChatEnabled]:
        return await self.repo.list()

    async def add(self, chat_id: int) -> CallPluginChatEnabled:
        obj = await self.get_by_chat_id(chat_id)
        if obj:
            return obj
        return await self.repo.add(chat_id)

    async def delete(self, obj: CallPluginChatEnabled) -> None:
        await self.repo.delete(obj)