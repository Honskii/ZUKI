from sqlalchemy.ext.asyncio import AsyncSession

from ..services.call import (
    CallPluginChatEnabledService,
    CallPluginChatMemberUnregService
)
from ..repositories.call import (
    CallPluginChatEnabledRepository,
    CallPluginChatMemberUnregRepository,
)

class CallPluginChatEnabledServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create(self) -> CallPluginChatEnabledService:
        return CallPluginChatEnabledService(
            repo=CallPluginChatEnabledRepository(self.session),
        )

class CallPluginChatMemberUnregServiceFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create(self) -> CallPluginChatMemberUnregService:
        return CallPluginChatMemberUnregService(
            repo=CallPluginChatMemberUnregRepository(self.session),
        )