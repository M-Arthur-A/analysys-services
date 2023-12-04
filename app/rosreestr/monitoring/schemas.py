from pydantic import BaseModel, ConfigDict


class SOrderMon(BaseModel):
    project:              str
    monitoring_cadastral: str
    monitoring_intense:   int
    monitoring_duration:  int
