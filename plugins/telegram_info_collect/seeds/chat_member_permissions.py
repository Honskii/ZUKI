from sqlalchemy import event
from ..models.chat_member import ChatMemberPermission

@event.listens_for(ChatMemberPermission.__table__, "after_create")
def insert_initial_roles(target, connection, **kw):
    connection.execute(
        target.insert(),
        [
            {"category": "user_info_collect", "name": "change state", "level": 6},

        ]
    )
