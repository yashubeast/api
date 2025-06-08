from datetime import datetime

from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from decimal import Decimal

from models import EquityBank
from models import DiscordMessages

from utils.database.models import DiscordMessages

class discord:

	@staticmethod
	async def get_balance(
		db: AsyncSession,
		discord_id: int
	):
		result = await db.execute(
			select(EquityBank.coins)
			.where(EquityBank.discord_id == discord_id)
		)
		return result.scalar_one_or_none()

	@staticmethod
	async def get_discord_message_count(
		db: AsyncSession,
		discord_id: int,
		server_id: int | None = None
	):
		stmt = select(DiscordMessages).where(DiscordMessages.discord_id == discord_id)
		if server_id is not None:
			stmt = stmt.where(DiscordMessages.server_id == server_id)

		result = await db.execute(stmt)
		return result.scalar_one_or_none()

	@staticmethod
	async def get_or_create_equity_account(
		db: AsyncSession,
		discord_id: int,
		coins: Decimal
	):
		stmt = select(EquityBank).where(EquityBank.discord_id == discord_id)
		result = await db.execute(stmt)
		entry = result.scalar_one_or_none()

		if entry is None:
			entry = EquityBank(discord_id=discord_id, coins=coins)
			db.add(entry)
		else:
			await db.execute(
				update(EquityBank)
				.where(EquityBank.discord_id == discord_id)
				.values(coins=EquityBank.coins + coins)
			)
		await db.commit()
		return entry

	@staticmethod
	async def increment_discord_message_count(
		db: AsyncSession,
		discord_id: int,
		server_id: int,
		timestamp: datetime
	):
		stmt = insert(DiscordMessages).values(
			discord_id=discord_id,
			server_id=server_id,
			message_count=1,
			last_message=timestamp,
		).on_conflict_do_update(
			index_elements=["discord_id", "server_id"],
			set = {
				"message_count": DiscordMessages.message_count + 1,
				"last_message": timestamp
			}
		)
		await db.execute(stmt)
		await db.commit()