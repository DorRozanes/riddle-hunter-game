from pydantic import BaseModel
from typing import Union

class PointSchema(BaseModel):
    latitude: float
    longitude: float

class BoundingBox2Point(BaseModel):
    north_east: PointSchema
    south_west: PointSchema

class BoundingBox4Point(BaseModel):
    north_west: PointSchema
    north_east: PointSchema
    south_west: PointSchema
    south_east: PointSchema

BoundingBox = Union[BoundingBox2Point, BoundingBox4Point]

class PlaceSchema(BaseModel):
    name: str
    google_place_id: str | None
    place_types: list[str] | None
    bounding_box: BoundingBox