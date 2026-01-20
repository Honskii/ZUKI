from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Identity, func
from sqlalchemy.orm import relationship

from .enums import ChatTypeEnum, Enum
from plugins.db_manager import Base

class Chat(Base):
    __tablename__ = "chats"
    id = Column(BigInteger, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    tg_id = Column(BigInteger, unique=True)
    name = Column(String(128), nullable=True)
    link = Column(String(32), index=True)
    type = Column(Enum(ChatTypeEnum, name="chat_type_enum"), nullable=False)
    activated = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    members = relationship("ChatMember", back_populates="chat")
