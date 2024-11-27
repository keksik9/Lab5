from pydantic import BaseModel
from typing import List, Optional

class Node(BaseModel):
    id: int
    label: Optional[str] = None
    name: Optional[str] = None
    screen_name: Optional[str] = None
    sex: Optional[int] = None
    city: Optional[str] = None

class Relationship(BaseModel):
    type: str
    end_node_id: int

class InsertRequest(BaseModel):
    node: Node
    relationships: List[Relationship]