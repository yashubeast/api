from fastapi import FastAPI, Depends, Query, Path
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import database, models, schemas, crud
from typing import Optional
from sqlalchemy import func
from sqlalchemy.future import select
from models import UserMessageCount
from routers.equity.msg_bank import router as message_router

app = FastAPI()

@app.on_event("startup")
async def startup():
	async with database.engine.begin() as conn:
		await conn.run_sync(models.Base.metadata.create_all)

app.include_router(message_router, prefix="/equity")