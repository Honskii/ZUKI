from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def add(
        self,
        tg_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        is_bot: bool,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_bot=is_bot,
            is_superuser=is_superuser,
        )
        self.session.add(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)

