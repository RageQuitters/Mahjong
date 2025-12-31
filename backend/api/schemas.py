from pydantic import BaseModel
from typing import List, Optional

class HandRequest(BaseModel):
    concealed: List[str]
    flowers: Optional[List[str]] = []
    display: Optional[List[str]] = []

class DiscardResponse(BaseModel):
    winning: bool
    best_discard: Optional[str] = None
    tai: Optional[int] = None