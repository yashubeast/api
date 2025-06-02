from fastapi import FastAPI, Depends, Query, Path
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import database, models, schemas, crud
from typing import Optional
from sqlalchemy import func
from sqlalchemy.future import select
from models import UserMessageCount

app = FastAPI()

@app.on_event("startup")
async def startup():
	async with database.engine.begin() as conn:
		await conn.run_sync(models.Base.metadata.create_all)
	
@app.post("/messages/add")
async def add_user_message(
	data: schemas.MessageUpdate,
	db: AsyncSession = Depends(database.get_db)
):
	user = await crud.alter_message_count(db, data.user_id, data.server_id)
	return {
		"user_id": user.user_id,
		"server_id": user.server_id,
		"message_count": user.message_count
	}

@app.post("/messages/remove")
async def remove_user_message(
	data: schemas.MessageUpdate,
	db: AsyncSession = Depends(database.get_db)
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

@app.get("/messages/{user_id}")
async def get_user_message_count(
	user_id: int = Path(..., description="id of user"),
	server_id: Optional[int] = Query(None, description="option id of server, else total message count across all servers"),
	db: AsyncSession = Depends(database.get_db)
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
			"total_message_count": total
		}