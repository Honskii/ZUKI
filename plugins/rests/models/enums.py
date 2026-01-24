import enum
import enum

from sqlalchemy import Enum as SAEnum

def Enum(enum_cls, name: str):
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda cls: [e.value for e in cls],
        native_enum=True
    )

class RestStateEnum(enum.Enum):
    BLOCKED = "blocked"
    ACTIVE = "active"