from sqlalchemy.ext.asyncio import AsyncSession

from ..services.chat import ChatService
from ..repositories.chat import ChatRepository


class ChatServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create(self) -> ChatService:
        return ChatService(
            chat_repo=ChatRepository(self.session),
        )