from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_input: str


class ChatResponse(BaseModel):
    route: str
    output: str
