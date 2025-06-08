import math

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from decimal import Decimal
from decimal import ROUND_HALF_UP

from starlette.responses import PlainTextResponse

import utils.database.schemas as schemas
from utils.database.crud import discord as crud_discord
from utils.database.models import EquityBank
from utils.database.init_db import main_db

router = APIRouter()

@router.get("/balance/{discord_id}")
async def get_balance(
	discord_id: int,
	db: AsyncSession = main_db
):
	coins = crud_discord.get_balance(db, discord_id)
	if coins is None:
		raise HTTPException(status_code=404, detail="user not found")
	return {
		"discord_id": discord_id,
		"balance": coins
	}

@router.post("pay")
async def pay(
	data: schemas.DiscordPay,
	db: AsyncSession = main_db
):
	sender_balance = crud_discord.get_balance(db, data.sender_id)
	receiver_balance = crud_discord.get_balance(db, data.receiver_id)

	if sender_balance is None or receiver_balance is None:
		raise HTTPException(status_code=404, detail="user not found")

	if sender_balance < data.amount:
		raise HTTPException(status_code=400, detail="not enough coins")

	sender_balance -= data.amount
	receiver_balance += data.amount

	await crud_discord.get_or_create_equity_account(db, data.sender_id, -sender_balance)
	await crud_discord.get_or_create_equity_account(db, data.receiver_id, receiver_balance)
	return {"sender_balance": sender_balance, "receiver_balance": receiver_balance}

@router.get("/leaderboard")
async def get_leaderboard(
	db: AsyncSession = main_db
):
	result = await db.execute(
		select(EquityBank.discord_id, EquityBank.coins)
		.order_by(EquityBank.coins.desc())
	)
	leaderboard = result.all()
	if not leaderboard:
		return PlainTextResponse("not even a single user in the bank", status_code=404)
	return leaderboard[:10]

@router.post("/formula")
async def calculate_equity(
	data: schemas.DiscordMessageEvaluation,
	db: AsyncSession = main_db,
):
	user = await crud_discord.get_discord_message_count(db, data.discord_id, data.server_id)
	if user is None:
		message_time_gap = 2
		message_count = 1
	else:
		message_time_gap = (data.timestamp - user.last_message).total_seconds()
		message_count = user.message_count

	time_value = message_time_gap * 0.15
	if time_value > 1:
		overflowValue = 1.2 * (math.log(1 + (message_time_gap - 7 / 60)) / math.log(61))
		time_value = 1 + overflowValue

	total = data.message_length * (1 + (.001 * message_count)) * time_value
	total = Decimal(str(total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

	if total != 0:
		await crud_discord.get_or_create_equity_account(db, user.discord_id, total)
	
	await crud_discord.increment_discord_message_count(
		db,
		data.discord_id,
		data.server_id,
		data.timestamp,
	)

	return {
		"discord_id": user.discord_id,
		"server_id": user.server_id,
		"message_length": data.message_length,
		"last_message": user.last_message if user else 'never',
		"new_message": data.timestamp,
		"message_time_gap": message_time_gap,
		"message_count": message_count,
		"equity_gained": total
	}