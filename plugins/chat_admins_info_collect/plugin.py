from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone

from zuki.plugin import Plugin

from plugins.telegram_info_collect.factories.chat import ChatServiceFactory
from .jobs.sync_chat_admins_job import sync_chat_admins_job
from plugins.db_manager import UnitOfWork

class ChatAdminInfoCollectPlugin(Plugin):
    name = "chat_admins_info_collect"
    requires = ["db_manager", "telegram_info_collect"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_ids = []
        self.iteration = 0
        self.uow: UnitOfWork = None

    async def on_startup(self):
        scheduler = AsyncIOScheduler()

        self.uow = self.app.get_service("db_manager:uow_factory")
        if self.uow is None:
            raise RuntimeError("UnitOfWork factory is not available")

        scheduler.add_job(
            self.job,
            "interval",
            max_instances=1,
            minutes=10
        )

        scheduler.start()

        # apscheduler.schedulers.SchedulerAlreadyRunningError

    async def update_chat_ids(self):
        async with self.uow() as uow:
            chat_service = ChatServiceFactory(uow.session).create()
            new_chat_ids = set([chat.tg_id for chat in await chat_service.list()])
            old_chat_ids = set(self.chat_ids)
            self.chat_id = self.chat_ids.extend(list(new_chat_ids - old_chat_ids))

    async def job(self):
        await self.update_chat_ids()
        self.iteration = self.iteration % len(self.chat_ids)
        await sync_chat_admins_job(
            bot=self.app.bot,
            chat_id=int(self.chat_ids[self.iteration]),
            uow_fabric=self.uow
        )
        print(f"{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
              f"Chat admins sync job done for chat_id={self.chat_ids[self.iteration]}")
        self.iteration += 1
