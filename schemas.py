from pydantic import BaseModel

class MessageUpdate(BaseModel):
	user_id: int
	server_id: int