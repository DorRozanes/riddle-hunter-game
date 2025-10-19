from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import select
from typing import List

from models import Place
from schemas.basic_location import PlaceSchema
from services.location_services import log_user_location, orm_place_to_schema, schema_place_to_orm
from utils.google_places import find_location_info_from_google
from utils.box_point_utils import make_bounding_box_schema, make_point_schema, point_schema_to_postgis
from schemas.location import PlaceQueryOut, PlaceQuery, PlaceCreate
from dependencies import get_current_user, get_db
from enums.type_priority import TYPE_PRIORITY

router = APIRouter(prefix="/api/locations", tags=["locations"])

def select_place (candidates: List):
    candidate_score = []
    for candidate in candidates:
        specific_score = 1000
        for place_type in candidate.place_types:
            specific_score = min(specific_score, TYPE_PRIORITY.index(place_type))
        candidate_score.append(specific_score)
    chosen_type = TYPE_PRIORITY[min(candidate_score)]
    for candidate in candidates:
        if chosen_type in candidate.place_types:
            return candidate
    return None

def insert_places_into_db (db, places):
    for place in places:
        print ("-------> Debug. Place:")
        print (place)
        stmt = select(Place).where(Place.google_place_id==place["place_id"])
        found_places = db.execute(stmt).scalars().all()
        if not found_places:

            if "viewport" in place["geometry"]:
                bbox = make_bounding_box_schema(place["geometry"]["viewport"])
            else:
                bbox = make_bounding_box_schema(place["geometry"]["location"])
            new_place = PlaceSchema(
                name=place["name"],
                place_types=place["types"],
                google_place_id=place["place_id"],
                bounding_box=bbox
            )
            print("-------> Debug. New Place:")
            print(new_place)
            db_place = schema_place_to_orm(new_place)

            db.add(db_place)
            db.commit()
            db.refresh(db_place)
            print("-------> Debug. Finished inserting")

@router.post("/", response_model=PlaceQueryOut)
def check_location(
    location_in: PlaceQuery,
    db: Session = Depends(get_db)
):
    print ("Checking location info")
    point = make_point_schema({
        "lat": location_in.point.latitude,
        "lng": location_in.point.longitude
        })
    postgis_point = point_schema_to_postgis(point)

    # Always query Google for now, and insert all results into the database
    # We'll manage caching later
    google_places = find_location_info_from_google(point)
    if not google_places:
        raise HTTPException(status_code=404, detail="No place found")

    insert_places_into_db(db, google_places)

    # Search the database
    stmt = select(Place).where(Place.bounding_box.ST_Contains(postgis_point))
    found_places = db.execute(stmt).scalars().all()
    place_info = select_place(found_places)
    if place_info:
        return PlaceQueryOut(place=orm_place_to_schema(place_info))
    else:
        return HTTPException(status_code=404, detail="No place found")