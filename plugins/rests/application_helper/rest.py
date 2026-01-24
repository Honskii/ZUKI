from datetime import datetime, date, timezone, tzinfo
from plugins.db_manager import UnitOfWork

from ..domains.rest import ChatMemberRestDomain
from ..factories.rest import ChatMemberRestServiceFactory

async def get_current_rests(
    uow_factory: UnitOfWork,
    tg_user_id: int,
    tg_chat_id: int,
    from_date: date,
    app_tzinfo: tzinfo
):
    async with uow_factory() as uow:
        rest_service = ChatMemberRestServiceFactory(uow.session).create()
        rests_from_db = await rest_service.get_by_tg_ids(
            tg_user_id=tg_user_id,
            tg_chat_id=tg_chat_id,
            from_date=from_date
        )

    rests = await ChatMemberRestDomain.filter_and_format_rests(
        rests_from_db=rests_from_db,
        app_tzinfo=app_tzinfo)

    return rests