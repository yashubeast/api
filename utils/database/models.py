from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint
from sqlalchemy import Numeric
from sqlalchemy import text
from sqlalchemy import TIMESTAMP
from sqlalchemy import ForeignKey

from utils.database.init_db import Base

class EquityBank(Base):
	__tablename__ = "equity_bank"

	discord_id = Column(BigInteger, primary_key=True, nullable=False)
	coins = Column(Numeric(precision=20, scale=2), server_default=text("0"), nullable=False)

	__table_args__ = (
		CheckConstraint("coins >= 0", name="check_coins_non_negative"),
	)

	def __repr__(self):
		return (
			f"<{self.__class__.__name__}(id={self.id}, "
			f"discord_id={self.discord_id}, "
			f"coins={self.coins})>"
		)
	
	def __str__(self):
		return (
			f"user {self.discord_id} has {self.coins} coins in the {self.__class__.__name__}"
		)

class DiscordMessages(Base):
	__tablename__ = "discord_messages"

	discord_id = Column(BigInteger, ForeignKey("equity_bank.discord_id", ondelete="CASCADE"), primary_key=True, nullable=False)
	server_id = Column(BigInteger, nullable=False)
	message_count = Column(Integer, server_default=text("0"), nullable=False)
	last_message = Column(TIMESTAMP(timezone=True), nullable=False)

	__table_args__ = (UniqueConstraint("user_id", "server_id", name="uix_user_server"),)

	def __repr__(self):
		return (
			f"<{self.__class__.__name__}(id={self.id}, "
			f"user_id={self.user_id}, "
			f"server_id={self.server_id}, "
			f"message_count={self.message_count})>"
		)
	
	def __str__(self):
		return (
			f"user {self.user_id} in server {self.server_id} has {self.message_count} messages"
		)
