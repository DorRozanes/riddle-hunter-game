from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.basic_location import PointSchema

class EnemySchema(BaseModel):
    id: int
    enemy_type: str
    location: PointSchema
    expires_at: datetime
    defeated: bool

    class Config:
        from_attributes = True

class EnemyDetailSchema(EnemySchema):
    riddle: str

class EnemyDefeatRequest(BaseModel):
    enemy_id: int
    answer: str


class EnemyDefeatResponse(BaseModel):
    success: bool
    message: str
    new_score: Optional[int] = None
    enemy: Optional[EnemySchema] = None