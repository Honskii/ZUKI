from typing import Optional, List

from ..models.chat_member import ChatMember, ChatMemberRole, ChatMemberPermission
from ..models.enums import ChatMemberStatusEnum
from ..repositories.chat_member import (
    ChatMemberRepository, ChatMemberRoleRepository,
    ChatMemberPermissionRepository
)
from ..services.user import UserService
from ..services.chat import ChatService

class ChatMemberRoleService:
    """
    Сервис ролей участников чата
    """
    def __init__(self, chat_member_role_repo: ChatMemberRoleRepository):
        self.chat_member_role_repo = chat_member_role_repo

    async def get(self, role_id: int) -> Optional[ChatMemberRole]:
        return await self.chat_member_role_repo.get(role_id)

    async def get_by_name(self, name: str) -> Optional[ChatMemberRole]:
        return await self.chat_member_role_repo.get_by_name(name)

    async def list(self) -> List[ChatMemberRole]:
        return await self.chat_member_role_repo.list()

    async def put(self, name: str, level: int) -> ChatMemberRole:
        """
        Создать роль, если её ещё нет, иначе вернуть существующую
        """
        role = await self.get_by_name(name)
        if role:
            return role

        role = await self.chat_member_role_repo.add(name=name, level=level)
        return role

    async def delete(self, role: ChatMemberRole) -> None:
        await self.chat_member_role_repo.delete(role)

    async def get_members(self, role_id: int) -> List[ChatMember]:
        """
        Получить всех участников, связанных с этой ролью
        """
        return await self.chat_member_role_repo.get_members(role_id)

class ChatMemberPermissionService:
    """
    Сервис разрешений для участников чата
    """
    def __init__(self, chat_member_permission_repo: ChatMemberPermissionRepository):
        self.chat_member_permission_repo = chat_member_permission_repo

    async def get(self, permission_id: int) -> Optional[ChatMemberPermission]:
        return await self.chat_member_permission_repo.get(permission_id)

    async def get_by_name(self, category: str, name: str) -> Optional[ChatMemberPermission]:
        return await self.chat_member_permission_repo.get_by_name(category, name)

    async def list(self) -> List[ChatMemberPermission]:
        return await self.chat_member_permission_repo.list()

    async def put(self, category: str, name: str, level: int) -> ChatMemberPermission:
        """
        Создать разрешение, если его нет, иначе вернуть существующее
        """
        permission = await self.get_by_name(category, name)
        if permission:
            return permission

        return await self.chat_member_permission_repo.add(category, name, level)

    async def delete(self, permission: ChatMemberPermission) -> None:
        await self.chat_member_permission_repo.delete(permission)

    async def is_allowed(self, permission: ChatMemberPermission, role_level: int) -> bool:
        """
        Проверка: доступна ли роль с данным уровнем к разрешению
        """
        return role_level >= permission.level

class ChatMemberService:
    """
    Общий сервис участников чата, ролей и разрешений
    """
    def __init__(
        self,
        user_service: UserService,
        chat_service: ChatService,
        chat_member_repo: ChatMemberRepository,
        role_service: ChatMemberRoleService,
        permission_service: ChatMemberPermissionService,
    ):
        self.user_service = user_service
        self.chat_service = chat_service
        self.chat_member_repo = chat_member_repo
        self.role_service = role_service
        self.permission_service = permission_service

    # --- Работа с участниками ---
    async def get(self, member_id: int) -> Optional[ChatMember]:
        return await self.chat_member_repo.get(member_id)

    async def get_by_user_and_chat_tg_ids(self, user_tg_id: int, chat_tg_id: int) -> Optional[ChatMember]:
        user = await self.user_service.get_by_tg_id(user_tg_id)
        chat = await self.chat_service.get_by_tg_id(chat_tg_id)
        if not user or not chat:
            return None
        return await self.chat_member_repo.get_by_user_and_chat(user.id, chat.id)

    async def list_by_chat_tg_id(self, chat_tg_id: int, statuses: List[str]) -> List[ChatMember]:
        chat = await self.chat_service.get_by_tg_id(chat_tg_id)
        return await self.chat_member_repo.list_by_chat(chat_id=chat.id, statuses=statuses)

    async def list_by_user_tg_id(self, user_tg_id: int) -> List[ChatMember]:
        user = await self.user_service.get_by_tg_id(user_tg_id)
        return await self.chat_member_repo.list_by_user(user.id)

    async def put(
        self,
        user_tg_id: int,
        chat_tg_id: int,
        status: ChatMemberStatusEnum = ChatMemberStatusEnum.MEMBER,
        role_id: Optional[int] = None,
        title: Optional[str] = None,
    ) -> ChatMember:
        member = await self.get_by_user_and_chat_tg_ids(user_tg_id, chat_tg_id)
        if role_id is None:
            if member:
                role = await self.get_role(member.id)
                if role is None:
                    role_id = 0
                else:
                    role_id = role.id

        if member:
            member.status = status
            member.role_id = role_id
            member.title = title
            await self.chat_member_repo.session.flush()
            return member
        user = await self.user_service.get_by_tg_id(user_tg_id)
        chat = await self.chat_service.get_by_tg_id(chat_tg_id)
        return await self.chat_member_repo.add(user.id, chat.id, status, role_id, title)

    async def delete(self, member: ChatMember) -> None:
        await self.chat_member_repo.delete(member)

    # --- Работа с ролями ---
    async def get_role(self, member_id: int) -> Optional[ChatMemberRole]:
        member = await self.get(member_id)
        if not member:
            return None
        return await self.role_service.get(member.role_id)

    async def set_role(self, member_id: int, role_id: int) -> Optional[ChatMember]:
        member = await self.get(member_id)
        if not member:
            return None
        member.role_id = role_id
        await self.chat_member_repo.session.flush()
        return member

    # --- Проверка разрешений ---
    async def has_permission(self, member_id: int, category: str, name: str) -> bool:
        """
        Проверка: есть ли у участника право по категории/имени
        """
        role = await self.get_role(member_id)
        permission = await self.permission_service.get_by_name(category, name)
        if not role:
            return False
        return await self.permission_service.is_allowed(permission, role.level)

    async def list_permissions(self, member_id: int) -> List[ChatMemberPermission]:
        """
        Получить все разрешения, доступные участнику по его уровню роли
        """
        role = await self.get_role(member_id)
        if not role:
            return []
        all_permissions = await self.permission_service.list()
        return [perm for perm in all_permissions if role.level >= perm.level]

    async def get_user(self, chat_member: ChatMember):
        user = await self.user_service.get(chat_member.user_id)
        return user

    async def get_chat(self, chat_member: ChatMember):
        chat = await self.chat_service.get(chat_member.chat_id)
        return chat