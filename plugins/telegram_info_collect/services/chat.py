from typing import Optional, List
from ..models.chat import Chat
from ..repositories.chat import ChatRepository

class ChatService:
    """
    Сервис чатов
    """
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def get(self, chat_id: int) -> Optional[Chat]:
        return await self.chat_repo.get(chat_id)

    async def get_by_tg_id(self, tg_id: int) -> Optional[Chat]:
        return await self.chat_repo.get_by_tg_id(tg_id)

    async def list(self) -> List[Chat]:
        return await self.chat_repo.list()

    async def put(
        self,
        tg_id: int,
        name: str,
        type,
        link: Optional[str] = None,
        activated: bool = False,
    ) -> Chat:
        """
        Создать чат, если его нет, иначе обновить существующий
        """
        chat = await self.get_by_tg_id(tg_id)
        if chat:
            chat.name = name
            chat.link = link
            chat.type = type
            chat.activated = activated
            # flush/commit будет на уровне UnitOfWork
            return chat

        return await self.chat_repo.add(
            tg_id=tg_id,
            name=name,
            link=link,
            type=type,
            activated=activated,
        )

    async def delete(self, chat: Chat) -> None:
        await self.chat_repo.delete(chat)