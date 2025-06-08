import os

from fastapi import Depends

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

with open("/run/secrets/PGPASS", "r") as f:
	db_pass = f.read().strip()
DB_URL = f"postgresql+asyncpg://admin:{db_pass}@postgres:5432/api"

engine = create_async_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
	async with SessionLocal() as session:
		yield session

main_db = Depends(get_db)