from sqlalchemy import Column, BigInteger, DateTime, Identity, ForeignKey, func

from plugins.db_manager import Base

class CallPluginChatMemberUnregModel(Base):
    __tablename__ = "call__chat_members_unreg"
    id = Column(BigInteger, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    chat_member_id = Column(BigInteger, ForeignKey("chat_members.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class CallPluginChatEnabled(Base):
    __tablename__ = "call__chats_enabled"
    id = Column(BigInteger, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
