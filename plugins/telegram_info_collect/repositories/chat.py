from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.chat import Chat


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, chat_id: int) -> Optional[Chat]:
        result = await self.session.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tg_id(self, tg_id: int) -> Optional[Chat]:
        result = await self.session.execute(
            select(Chat).where(Chat.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[Chat]:
        result = await self.session.execute(select(Chat))
        return result.scalars().all()

    async def add(
        self,
        tg_id: int,
        name: Optional[str],
        link: Optional[str],
        type,
        activated: bool = False,
    ) -> Chat:
        chat = Chat(
            tg_id=tg_id,
            name=name,
            link=link,
            type=type,
            activated=activated,
        )
        self.session.add(chat)
        return chat

    async def delete(self, chat: Chat) -> None:
        await self.session.delete(chat)