from pydantic import BaseModel

class SubscribeRequest(BaseModel):
    user_id: int
    channels_payload: set[int]

class UnsubscribeRequest(BaseModel):
    user_id: int
    channels_payload: set[int]

class ResponseToRAG(BaseModel):
    channel_id: int
    texts: str

class RemoveSourceResponseToRAG(BaseModel):
    channel_id: int
class CollectedMessage(BaseModel):
    chat_id: int
    text: str