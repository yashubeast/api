from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserMessageCount
from typing import Optional

async def alter_message_count(db: AsyncSession, user_id: int, server_id: int, increment: int = 1):
	result = await db.execute(
		select(UserMessageCount).where(
			UserMessageCount.user_id == user_id,
			UserMessageCount.server_id == server_id
		)
	)
	user = result.scalar_one_or_none()

	if user:
		user.message_count += increment
		# prevent negatives
		if user.message_count < 0:
			user.message_count = 0
	else:
		# only create if increment is positive
		if increment > 0:
			user = UserMessageCount(
				user_id=user_id,
				server_id=server_id,
				message_count=increment
			)
			db.add(user)
		else:
			return None
	
	await db.commit()
	await db.refresh(user)
	return user

async def get_message_count(db: AsyncSession, user_id: int, server_id: Optional[int] = None):
	if server_id is not None:
		result = await db.execute(
			select(UserMessageCount).where(
				UserMessageCount.user_id == user_id,
				UserMessageCount.server_id == server_id
			)
		)
		return result.scalar_one_or_none()
	else:

		result = await db.execute(
			select(func.sum(UserMessageCount.message_count))
			.where(UserMessageCount.user_id == user_id)
		)
		total = result.scalar_one_or_none()
		return total