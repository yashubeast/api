from pydantic import BaseModel

class MessageUpdate(BaseModel):
	user_id: int
	server_id: int

class FormulaData(BaseModel):
	user_id: int
	server_id: int
	message_length: int
	message_time_gap: float