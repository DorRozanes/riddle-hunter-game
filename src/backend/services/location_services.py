from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon
from ..models import Place, LocationHistory
from ..utils.google_places import find_location_info_from_google
from ..utils.box_point_utils import bbox_schema_to_postgis_polygon
from ..schemas.basic_location import PlaceSchema, PointSchema, BoundingBox4Point

def find_local_place(db: Session, lat: float, lng: float) -> Place | None:
    return (
        db.query(Place)
        .filter(Place.lat_min <= lat, Place.lat_max >= lat,
                Place.lng_min <= lng, Place.lng_max >= lng)
        .first()
    )

def log_user_location(db: Session, user_id: int, lat: float, lng: float) -> LocationHistory:
    # Check local cache first
    place = find_local_place(db, lat, lng)
    if place:
        place_type = place.place_type
    else:
        # Call Google and save new place
        result = find_location_info_from_google(lat, lng)
        if result is None:
            place_type = None
        else:
            place_type, bbox = result
            new_place = Place(
                name="Unknown",  # optional: can store Google name
                place_type=place_type,
                lat_min=bbox["lat_min"],
                lat_max=bbox["lat_max"],
                lng_min=bbox["lng_min"],
                lng_max=bbox["lng_max"]
            )
            db.add(new_place)
            db.commit()

    # Log user location
    location = LocationHistory(
        user_id=user_id,
        latitude=lat,
        longitude=lng,
        place_type=place_type
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

def orm_place_to_schema(place: Place) -> PlaceSchema:
    """
    Convert a SQLAlchemy Place ORM row into a PlaceSchema.
    Handles PostGIS bounding_box -> BoundingBox2Point or BoundingBox4Point.
    """

    bounding_box = None

    if place.bounding_box is not None:
        shp = to_shape(place.bounding_box)  # shapely Polygon
        if not isinstance(shp, Polygon):
            raise TypeError(f"Expected Polygon, got {type(shp)}")

        # Shapely polygon exterior coords is a sequence [(x1,y1), (x2,y2), ...]
        coords = list(shp.exterior.coords)

        # Get min/max corners
        minx, miny, maxx, maxy = shp.bounds

        bounding_box = BoundingBox4Point(
            south_west=PointSchema(latitude=miny, longitude=minx),
            south_east=PointSchema(latitude=miny, longitude=maxx),
            north_east=PointSchema(latitude=maxy, longitude=maxx),
            north_west=PointSchema(latitude=maxy, longitude=minx),
        )

    return PlaceSchema(
        name=place.name,
        google_place_id=place.google_place_id,
        place_types=place.place_types,
        bounding_box=bounding_box,
    )

def schema_place_to_orm(place: PlaceSchema) -> Place:
    bbox = bbox_schema_to_postgis_polygon(place.bounding_box)
    return Place(
        name=place.name,
        google_place_id=place.google_place_id,
        place_types=place.place_types,
        bounding_box=bbox,
    )