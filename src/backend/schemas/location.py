from pydantic import BaseModel
from datetime import datetime
from schemas.basic_location import PointSchema, PlaceSchema

class PlaceCreate(BaseModel):
    place: PlaceSchema

class PlaceQuery(BaseModel):
    point: PointSchema

class PlaceQueryOut(BaseModel):
    place: PlaceSchema

class LocationHistoryCreate(BaseModel):
    point: PointSchema
