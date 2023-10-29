from pydantic import BaseModel, ConfigDict
from datetime import date


class SOrder(BaseModel):
    cadastral:      int
    cadastral_type: str
    status:         str
    detail:         str
    created_at:     date


class SOrders(BaseModel):
    id:             int
    name:           str
    is_ready:       bool
    orders:         list[SOrder]

class SOrderFull(BaseModel):
    id:             str
    query_id:       int
    session_id:     str
    cadastral:      str
    cadastral_type: str
    status:         str
    status_txt:     str
    is_ready:       bool
    created_at:     date
    modified_at:    date

class SOrdersFull(BaseModel):
    orders: list[SOrderFull]

class SReorder(BaseModel):
    query_id: int


class SDownload(BaseModel):
    query_id:   int
    query_name: str

class SQuery(BaseModel):
    project: str | None
    query_s: str | None
    query_h: str | None
