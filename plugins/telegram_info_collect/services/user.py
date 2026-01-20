from typing import Optional, List
from ..models.user import User
from ..repositories.user import UserRepository

class UserService:
    """
    Сервис пользователей
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get(user_id)

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        return await self.user_repo.get_by_tg_id(tg_id)

    async def list(self) -> List[User]:
        return await self.user_repo.list()

    async def put(
        self,
        tg_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        is_bot: bool,
        is_superuser: bool = False,
    ) -> User:
        user = await self.get_by_tg_id(tg_id)
        if user:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_bot = is_bot
            user.is_superuser = is_superuser
            return user

        return await self.user_repo.add(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_bot=is_bot,
            is_superuser=is_superuser,
        )

    async def delete(self, user: User) -> None:
        await self.user_repo.delete(user)