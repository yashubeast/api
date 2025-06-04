import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

os.makedirs("./assets", exist_ok=True)

DB_URL = "sqlite+aiosqlite:///./assets/main.db"

engine = create_async_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
	async with SessionLocal() as session:
		yield session