from fastapi import APIRouter, Depends, Path, Query
from typing import Optional
from starlette.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models import UserMessageCount, EquityBank
import database, models, schemas, crud, math
from decimal import Decimal, ROUND_HALF_UP

router = APIRouter(prefix="/coin")

@router.get("/balance/{user_id}")
async def balance(
	user_id: int = Path(..., description="id of user"),
	db: AsyncSession = Depends(database.get_db)
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