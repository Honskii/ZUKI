from sqlalchemy import Column, BigInteger, DateTime, Boolean, Identity, ForeignKey, func
from sqlalchemy.orm import relationship

from .enums import RestStateEnum, Enum
from plugins.db_manager import Base

class ChatMemberRest(Base):
    __tablename__ = "chat_member_rests"
    id = Column(BigInteger, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    chat_member_id = Column(BigInteger, ForeignKey("chat_members.id"), nullable=False)
    state = Column(Enum(RestStateEnum, name="rest_state_enum"), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
