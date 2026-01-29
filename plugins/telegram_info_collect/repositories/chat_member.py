from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.chat_member import ChatMember, ChatMemberRole, ChatMemberPermission
from ..models.enums import ChatMemberStatusEnum

class ChatMemberRoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, role_id: int) -> Optional[ChatMemberRole]:
        result = await self.session.execute(
            select(ChatMemberRole).where(ChatMemberRole.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[ChatMemberRole]:
        result = await self.session.execute(
            select(ChatMemberRole).where(ChatMemberRole.name == name)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[ChatMemberRole]:
        result = await self.session.execute(select(ChatMemberRole))
        return result.scalars().all()

    async def add(self, name: str, level: int) -> ChatMemberRole:
        role = ChatMemberRole(name=name, level=level)
        self.session.add(role)
        return role

    async def update(self, role: ChatMemberRole) -> ChatMemberRole:
        self.session.add(role)
        return role

    async def delete(self, role: ChatMemberRole) -> None:
        await self.session.delete(role)

    async def get_members(self, role_id: int) -> List[ChatMember]:
        """Получить всех участников, с этой ролью по relationship"""
        result = await self.session.execute(
            select(ChatMember).where(ChatMember.role_id == role_id)
        )
        return result.scalars().all()

class ChatMemberPermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, permission_id: int) -> Optional[ChatMemberPermission]:
        result = await self.session.execute(
            select(ChatMemberPermission).where(ChatMemberPermission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, category: str, name: str) -> Optional[ChatMemberPermission]:
        result = await self.session.execute(
            select(ChatMemberPermission).where(
                ChatMemberPermission.category == category,
                ChatMemberPermission.name == name
            )
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[ChatMemberPermission]:
        result = await self.session.execute(select(ChatMemberPermission))
        return result.scalars().all()

    async def delete(self, permission: ChatMemberPermission) -> None:
        await self.session.delete(permission)

class ChatMemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, member_id: int) -> Optional[ChatMember]:
        result = await self.session.execute(
            select(ChatMember).where(ChatMember.id == member_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_chat(self, user_id: int, chat_id: int) -> Optional[ChatMember]:
        result = await self.session.execute(
            select(ChatMember).where(
                ChatMember.user_id == user_id,
                ChatMember.chat_id == chat_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_chat(self, chat_id: int, statuses: List[str] = []) -> List[ChatMember]:
        chat_members = select(ChatMember).where(ChatMember.chat_id == chat_id)
        if statuses:
            chat_members = chat_members.where(ChatMember.status.in_(statuses))
        result = await self.session.execute(chat_members)
        return result.scalars().all()

    async def list_by_user(self, user_id: int) -> List[ChatMember]:
        result = await self.session.execute(
            select(ChatMember).where(ChatMember.user_id == user_id)
        )
        return result.scalars().all()

    async def add(
        self,
        user_id: int,
        chat_id: int,
        status: ChatMemberStatusEnum = ChatMemberStatusEnum.MEMBER,
        role_id: int = 1,
        title: Optional[str] = None,
    ) -> None:
        member = ChatMember(
            user_id=user_id,
            chat_id=chat_id,
            status=status,
            role_id=role_id,
            title=title,
        )
        self.session.add(member)
        return member

    async def delete(self, member: ChatMember) -> None:
        await self.session.delete(member)

    async def get_role(self, member_id: int) -> Optional[ChatMemberRole]:
        result = await self.session.execute(
            select(ChatMemberRole).join(ChatMember).where(ChatMember.id == member_id)
        )
        return result.scalar_one_or_none()