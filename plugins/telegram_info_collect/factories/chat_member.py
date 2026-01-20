from sqlalchemy.ext.asyncio import AsyncSession

from ..services.user import UserService
from ..services.chat import ChatService
from ..services.chat_member import (
    ChatMemberService, ChatMemberRoleService,
    ChatMemberPermissionService
)
from ..repositories.user import UserRepository
from ..repositories.chat import ChatRepository
from ..repositories.chat_member import(
    ChatMemberRepository, ChatMemberRoleRepository,
    ChatMemberPermissionRepository
)

class ChatMemberServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create(self) -> ChatMemberService:
        return ChatMemberService(
            user_service=UserService(UserRepository(self.session)),
            chat_service=ChatService(ChatRepository(self.session)),
            chat_member_repo=ChatMemberRepository(self.session),
            role_service=ChatMemberRoleService(ChatMemberRoleRepository(self.session)),
            permission_service=ChatMemberPermissionService(ChatMemberPermissionRepository(self.session)),
        )
