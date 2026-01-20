from sqlalchemy import event
from ..models.chat_member import ChatMemberRole

@event.listens_for(ChatMemberRole.__table__, "after_create")
def insert_initial_roles(target, connection, **kw):
    connection.execute(
        target.insert(),
        [
            {"id": 0, "name": "Default", "level": 1}
        ]
    )
    connection.execute(
        target.insert(),
        [
            {"name": "Moderator", "level": 2},
            {"name": "Sr. Moderator", "level": 3},
            {"name": "Administrator", "level": 4},
            {"name": "Sr. Administrator", "level": 5},
            {"name": "Owner", "level": 6},
            {"name": "Superuser", "level": 7},
        ]
    )
