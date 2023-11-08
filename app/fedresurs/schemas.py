from pydantic import BaseModel, ConfigDict
from datetime import date


class SQuery(BaseModel):
    query: str | None
