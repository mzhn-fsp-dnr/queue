from typing import List
from pydantic import BaseModel


class ServiceSchema(BaseModel):
    id: str
    name: str
    children: List["ServiceSchema"] = []


class WindowSchema(BaseModel):
    id: str
    name: str
    services: List["ServiceSchema"] = []


class OfficeResponse(BaseModel):
    id: str
    name: str
    address: str
    services: List[ServiceSchema] = []
    windows: List[WindowSchema] = []
