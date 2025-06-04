import math

from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query

from decimal import Decimal
from decimal import ROUND_HALF_UP

from starlette.responses import PlainTextResponse

from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

import utils.database.schemas as schemas
import utils.database.crud as crud
from utils.database.init_db import main_db
from utils.database.models import UserMessageCount
from utils.database.models import EquityBank

router = APIRouter()

@router.post("/add")
async def add_user_message(
	data: schemas.MessageUpdate,
	db: AsyncSession = main_db
):
	user = await crud.alter_message_count(db, data.user_id, data.server_id)
	return {
		"user_id": user.user_id,
		"server_id": user.server_id,
		"message_count": user.message_count
	}

@router.post("/remove")
async def remove_user_message(
	data: schemas.MessageUpdate,
	db: AsyncSession = main_db
):
	user = await crud.get_message_count(db, data.user_id, data.server_id)

	if user is None:
		return PlainTextResponse("no entry for user", status_code=404)
	
	# prevent going below 0
	if user.message_count > 0:
		user = await crud.alter_message_count(db, data.user_id, data.server_id, increment=-1)
	else:
		return PlainTextResponse("message count 0", status_code=400)
	
	return {
		"user_id": user.user_id,
		"server_id": user.server_id,
		"message_count": user.message_count
	}

@router.get("/{user_id}")
async def get_user_message_count(
	user_id: int = Path(..., description="id of user"),
	server_id: Optional[int] = Query(None, description="optional id of server, else total message count across all servers will be returned"),
	db: AsyncSession = main_db
):

	if server_id is not None:

		user = await crud.get_message_count(db, user_id, server_id)

		if user is None:
			return PlainTextResponse("no entry for user", status_code=404)
		
		return {
			"user_id": user.user_id,
			"server_id": user.server_id,
			"message_count": user.message_count
		}
	
	else:

		result = await db.execute(
			select(func.sum(UserMessageCount.message_count))
			.where(UserMessageCount.user_id == user_id)
		)
		total = result.scalar_one_or_none()
		if total is None:
			return PlainTextResponse("no entry for user", status_code=404)
		return {
			"user_id": user_id,
			"message_count": total
		}

@router.post("/formula")
async def formula(
	data: schemas.FormulaData,
	db: AsyncSession = main_db
):
	user = await crud.get_message_count(db, data.user_id, data.server_id)

	if user is None:
		return PlainTextResponse("no entry for user", status_code=404)
	
	time_value = data.message_time_gap * 0.15
	if time_value > 1:
		overflowValue = 1.2 * (math.log(1 + (data.message_time_gap - 7 / 60)) / math.log(61))
		time_value = 1 + overflowValue
	total = data.message_length * (1 + (.001 * user.message_count)) * time_value

	total = Decimal(str(total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

	if total != 0:
		exist = await db.execute(
			select(EquityBank).where(
				EquityBank.user_id == user.user_id
			)
		)
		exists = exist.scalar_one_or_none()

		if exists is None:
			# user doesn't exist in equity bank, create entry
			new_entry = EquityBank(
				user_id = user.user_id,
				coins = total
			)
			db.add(new_entry)
		else:
			# user exists, update coins
			await db.execute(
				update(EquityBank)
				.where(EquityBank.user_id == user.user_id)
				.values(coins=EquityBank.coins + total)
			)
		await db.commit()

	return {
		"user_id": user.user_id,
		"server_id": user.server_id,
		"message_length": data.message_length,
		"message_time_gap": data.message_time_gap,
		"message_count": user.message_count,
		"total": total
	}