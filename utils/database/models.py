from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint
from sqlalchemy import Numeric

from utils.database.init_db import Base

class UserMessageCount(Base):
	__tablename__ = "user_message_count"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(BigInteger, index=True, nullable=False)
	server_id = Column(BigInteger, index=True, nullable=False)
	message_count = Column(Integer, default=0)

	__table_args__ = (UniqueConstraint("user_id", "server_id", name="uix_user_server"),)

class EquityBank(Base):
	__tablename__ = "equity_bank"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(BigInteger, index=True, nullable=False)
	coins = Column(Numeric(precision=20, scale=2), index=True, nullable=False, default=0)

	__table_args__ = (
		CheckConstraint("coins >= 0", name="check_coins_non_negative"),
	)