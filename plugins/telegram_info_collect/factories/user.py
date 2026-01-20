from sqlalchemy.ext.asyncio import AsyncSession

from ..services.user import UserService
from ..repositories.user import UserRepository

class UserServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create(self) -> UserService:
        return UserService(
            user_repo=UserRepository(self.session),
        )
