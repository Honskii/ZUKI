from aiogram import Bot
from plugins.telegram_info_collect.factories.chat_member import ChatMemberServiceFactory
from plugins.telegram_info_collect.factories.user import UserServiceFactory
from plugins.db_manager import UnitOfWork

async def sync_chat_admins_job(
    bot: Bot,
    chat_id: int,
    uow_fabric: UnitOfWork
):
    admins = await bot.get_chat_administrators(chat_id)

    user = None
    async with uow_fabric() as uow:
        user_service = UserServiceFactory(uow.session).create()
        for admin in admins:
            user = await user_service.put(
                tg_id=admin.user.id,
                username=admin.user.username,
                first_name=admin.user.first_name,
                last_name=admin.user.last_name,
                is_bot=admin.user.is_bot,
                is_superuser=False
            )

    if user is None:
        return

    async with uow_fabric() as uow:
        chat_member_service = ChatMemberServiceFactory(uow.session).create()
        for admin in admins:
            await chat_member_service.put(
                user_tg_id=admin.user.id,
                chat_tg_id=chat_id,
                status=admin.status,
                title=getattr(admin, "custom_title", "admin"),
                role_id=1
            )
