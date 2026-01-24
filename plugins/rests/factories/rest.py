from sqlalchemy.ext.asyncio import AsyncSession

from plugins.telegram_info_collect.factories.chat_member import ChatMemberServiceFactory

from ..repositories.rest import ChatMemberRestRepository
from ..services.rest import ChatMemberRestsService


class ChatMemberRestServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create(self) -> ChatMemberRestsService:
        chat_member_service = ChatMemberServiceFactory(self.session).create()
        return ChatMemberRestsService(
            rests_repo = ChatMemberRestRepository(self.session),
            chat_member_service = chat_member_service
        )