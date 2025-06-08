from pydantic import BaseModel
from datetime import datetime

class DiscordMessageEvaluation(BaseModel):
	discord_id: int
	server_id: int
	message_length: int
	timestamp: datetime

class DiscordPay(BaseModel):
	sender_id: int
	receiver_id: int
	amount: float