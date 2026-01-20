from sqlalchemy import Column, BigInteger, Integer, String, DateTime, UniqueConstraint, ForeignKey, Identity, func
from sqlalchemy.orm import relationship

from plugins.db_manager import Base
from .enums import Enum, ChatMemberStatusEnum

class ChatMemberRole(Base):
    __tablename__ = "chat_member_roles"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True)
    name = Column(String, unique=True, nullable=False)
    level = Column(Integer, unique=True, nullable=False)

    chat_members = relationship("ChatMember", back_populates="role")

class ChatMemberPermission(Base):
    __tablename__ = "chat_member_permissions"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("category", "name", name="uq_permission_category_name"),)

class ChatMember(Base):
    __tablename__ = "chat_members"
    id = Column(BigInteger, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"))
    status = Column(
        Enum(ChatMemberStatusEnum, name="chat_member_status_enum"),
        nullable=False,
        default=ChatMemberStatusEnum.MEMBER.value)
    role_id = Column(Integer, ForeignKey("chat_member_roles.id"), nullable=False, default=1)
    title = Column(String(16))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="chats")
    chat = relationship("Chat", back_populates="members")
    role = relationship("ChatMemberRole", back_populates="chat_members")

    __table_args__ = (UniqueConstraint("user_id", "chat_id", name="uq_user_chat"),)
