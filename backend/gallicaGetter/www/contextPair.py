from pydantic import BaseModel


class ContextPair(BaseModel):
    ark_code: str
    term: str
