import math

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.responses import PlainTextResponse

from utils.database.models import EquityBank
from utils.database.init_db import main_db

router = APIRouter()

@router.get("/balance/{user_id}")
async def balance(
	db: AsyncSession = main_db,
	user_id: int = Path(..., description="id of user")
):
	result = await db.execute(
		select(EquityBank).where(EquityBank.user_id == user_id)
	)
	balance = result.scalar_one_or_none()

	if balance is None:
		return PlainTextResponse("no entry for user", status_code=404)
	
	return {
		"coins": math.floor(balance.coins)
	}