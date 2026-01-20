import enum

from sqlalchemy import Enum as SAEnum

def Enum(enum_cls, name: str):
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda cls: [e.value for e in cls],
        native_enum=True
    )

class ChatTypeEnum(enum.Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    FORUM = "forum"
    CHANEL = "chanel"
    OTHER = "other"

class ChatMemberStatusEnum(enum.Enum):
    BANNED = "banned"
    LEFT = "left"
    RESTRICTED = "resticted"
    PEDNING = "pending"
    MEMBER = "member"
    ADMINISTRATOR = "administrator"
    OWNER = "owner"

