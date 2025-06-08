import time

with open("/run/secrets/PGPASS", "r") as f:
	pgpass = f.read().strip()

while True:
	print(pgpass)
	time.sleep(3)