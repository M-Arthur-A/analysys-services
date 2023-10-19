from pydantic import BaseModel
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


class SReorder(BaseModel):
    query_id: int


class SDownload(BaseModel):
    query_id:   int
    query_name: str

class SQuery(BaseModel):
    project: str
    query_s: str
    query_h: str
