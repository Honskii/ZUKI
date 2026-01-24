from typing import List, Optional
from datetime import date
from ..models.rest import ChatMemberRest
from ..models.enums import RestStateEnum
from ..repositories.rest import ChatMemberRestRepository
from plugins.telegram_info_collect.services.chat_member import ChatMemberService

class ChatMemberRestsService:
    """
    Сервис для управления периодами отдыха участников чата
    """
    def __init__(
        self,
        rests_repo: ChatMemberRestRepository,
        chat_member_service: ChatMemberService,
    ):
        self.rests_repo = rests_repo
        self.chat_member_service = chat_member_service

    async def get(self, rest_id: int) -> Optional[ChatMemberRest]:
        return await self.rests_repo.get(rest_id)

    async def get_by_tg_ids(
        self,
        tg_user_id: int,
        tg_chat_id: int,
        states: List[str] = [],
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[ChatMemberRest]:
        chat_member = await self.chat_member_service.get_by_user_and_chat_tg_ids(tg_user_id, tg_chat_id)
        if not chat_member:
            return None

        return await self.rests_repo.get_by_chat_member_id(
            chat_member_id=chat_member.id,
            states=states,
            from_date=from_date,
            to_date=to_date,
        )

    async def list(self) -> List[ChatMemberRest]:
        return await self.rests_repo.list()

    async def put(
        self,
        tg_user_id: int,
        tg_chat_id: int,
        state: RestStateEnum,
        starts_at: date,
        ends_at: date,
        revoked: bool = False,
    ) -> ChatMemberRest:
        """
        Создать новый период отдыха
        """
        chat_member = await self.chat_member_service.get_by_user_and_chat_tg_ids(tg_user_id, tg_chat_id)
        if not chat_member:
            return None

        return await self.rests_repo.add(
            chat_member_id=chat_member.id,
            state=state,
            starts_at=starts_at,
            ends_at=ends_at,
            revoked=revoked,
        )

    async def delete(self, rest: ChatMemberRest) -> None:
        await self.rests_repo.delete(rest)

    