from enum import Enum

from pydantic import BaseModel, Field
from pydantic.networks import IPvAnyAddress

class Commands(Enum):
    start = 'start'
    stop = 'stop'

class RequestModel(BaseModel):
    command: Commands
    ip: IPvAnyAddress
    port: int = Field(ge=1024, le=65535)
    model: str