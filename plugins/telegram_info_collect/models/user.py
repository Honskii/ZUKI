from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Identity, func
from sqlalchemy.orm import relationship

from plugins.db_manager import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    tg_id = Column(BigInteger, unique=True)
    username = Column(String(32), index=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    is_bot = Column(Boolean, nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    chats = relationship("ChatMember", back_populates="user")
    # activity = relationship("Activity", back_populates="user")
