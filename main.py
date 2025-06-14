import routers

from fastapi import FastAPI

import utils.database.init_db as init_db
import utils.database.models as models

app = FastAPI()

@app.on_event("startup")
async def startup():
	init_db.init_engine()
	async with init_db.engine.begin() as conn:
		await conn.run_sync(models.Base.metadata.create_all)

for prefix, router in routers.collect_routers():
	app.include_router(router, prefix=prefix)