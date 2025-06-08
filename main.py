import routers

from fastapi import FastAPI

import utils.database.init_db as init_db
import utils.database.models as models

with open("/run/secrets/PGPASS", "r") as f:
	print(f.read().strip())

app = FastAPI()

@app.on_event("startup")
async def startup():
	async with init_db.engine.begin() as conn:
		await conn.run_sync(models.Base.metadata.create_all)

for prefix, router in routers.collect_routers():
	app.include_router(router, prefix=prefix)