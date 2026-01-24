from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..models.rest import ChatMemberRest, RestStateEnum

class ChatMemberRestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, rest_id: int) -> Optional[ChatMemberRest]:
        result = await self.session.execute(
            select(ChatMemberRest).where(ChatMemberRest.id == rest_id)
        )
        return result.scalar_one_or_none()

    async def get_by_chat_member_id(
        self,
        chat_member_id: int,
        states: List[str] = [],
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[ChatMemberRest]:
        query = select(ChatMemberRest).where(
            ChatMemberRest.chat_member_id == chat_member_id
        )

        if states:
            query = query.where(ChatMemberRest.state.in_(states))

        date_conditions = []
        if from_date:
            date_conditions.append(ChatMemberRest.ends_at >= from_date)
        if to_date:
            date_conditions.append(ChatMemberRest.starts_at <= to_date)
        if date_conditions:
            query = query.where(or_(*date_conditions))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list(self) -> List[ChatMemberRest]:
        result = await self.session.execute(select(ChatMemberRest))
        return result.scalars().all()

    async def add(
        self,
        chat_member_id: int,
        state: RestStateEnum,
        starts_at: date,
        ends_at: date,
        revoked: bool = False,
    ) -> ChatMemberRest:
        rest = ChatMemberRest(
            chat_member_id=chat_member_id,
            state=state,
            starts_at=starts_at,
            ends_at=ends_at,
            revoked=revoked,
        )
        self.session.add(rest)
        return rest

    async def delete(self, rest: ChatMemberRest) -> None:
        await self.session.delete(rest)