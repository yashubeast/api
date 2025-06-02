from sqlalchemy import Column, Integer, BigInteger, UniqueConstraint
from database import Base

class UserMessageCount(Base):
	__tablename__ = "user_message_count"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(BigInteger, index=True, nullable=False)
	server_id = Column(BigInteger, index=True, nullable=False)
	message_count = Column(Integer, default=0)

	__table_args__ = (UniqueConstraint("user_id", "server_id", name="uix_user_server"),)