from shapely.geometry import Polygon
from typing import Union, List
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point as ShapelyPoint
from geoalchemy2.elements import WKBElement
import math

# Your schemas
from ..schemas.basic_location import PointSchema, BoundingBox4Point, BoundingBox2Point, BoundingBox


### Bounding box utils
def make_bounding_box_schema(data: Union[dict, List[PointSchema]]) -> BoundingBox4Point:
    """
    Create a normalized BoundingBox4Point.

    Input can be:
    - Google viewport dict: {"northeast": {"lat": .., "lng": ..}, "southwest": {...}}
    - List of 2 PointSchema (must be NE+SW or NW+SE, order doesn't matter)
    - List of 4 PointSchema (any order, normalized to NW, NE, SW, SE)

    Returns:
        BoundingBox4Point
    """

    def to_tuple(p: PointSchema | dict) -> tuple[float, float]:
        """Convert PointSchema or dict into (lng, lat) tuple"""
        if isinstance(p, PointSchema):
            return (p.longitude, p.latitude)
        return (p["lng"], p["lat"])

    # --- Case 1: Google viewport dict ---
    if isinstance(data, dict) and "northeast" in data and "southwest" in data:
        ne = to_tuple(data["northeast"])
        sw = to_tuple(data["southwest"])
        nw = (sw[0], ne[1])
        se = (ne[0], sw[1])

    # --- Case 2: List of PointSchema ---
    elif isinstance(data, list):
        pts = [to_tuple(p) for p in data]

        if len(pts) == 2:
            p1, p2 = pts
            lngs = [p1[0], p2[0]]
            lats = [p1[1], p2[1]]
            if lngs[0]==lngs[1] or lats[0]==lats[1]:
                raise ValueError("Two points must be opposite corners (NE+SW or NW+SE)")

            minx, maxx = min(lngs), max(lngs)
            miny, maxy = min(lats), max(lats)

            # Candidate corners
            sw = (minx, miny)
            ne = (maxx, maxy)
            nw = (minx, maxy)
            se = (maxx, miny)

        elif len(pts) == 4:
            # Compute bounds
            lngs = [p[0] for p in pts]
            lats = [p[1] for p in pts]

            minx, maxx = min(lngs), max(lngs)
            miny, maxy = min(lats), max(lats)

            sw = (minx, miny)
            se = (maxx, miny)
            nw = (minx, maxy)
            ne = (maxx, maxy)

        else:
            raise ValueError("Expected 2 or 4 PointSchema objects in list")

    else:
        raise ValueError("Unsupported bounding box input format")

    # --- Build Pydantic BoundingBox4Point ---
    bbox = BoundingBox4Point(
        north_west=PointSchema(latitude=nw[1], longitude=nw[0]),
        north_east=PointSchema(latitude=ne[1], longitude=ne[0]),
        south_west=PointSchema(latitude=sw[1], longitude=sw[0]),
        south_east=PointSchema(latitude=se[1], longitude=se[0]),
    )

    return bbox

def bbox2_to_bbox4(bbox2: BoundingBox2Point) -> BoundingBox4Point:
    """
    Convert a BoundingBox2Point (north_east + south_west)
    into a BoundingBox4Point (nw, ne, sw, se).
    """
    ne = bbox2.north_east
    sw = bbox2.south_west

    # Derive other corners
    nw = PointSchema(latitude=ne.latitude, longitude=sw.longitude)
    se = PointSchema(latitude=sw.latitude, longitude=ne.longitude)

    return BoundingBox4Point(
        north_west=nw,
        north_east=ne,
        south_west=sw,
        south_east=se,
    )

def bbox_schema_to_postgis_polygon(bbox: BoundingBox):
    """
    Converts a BoundingBox object (2-point or 4-point) into a PostGIS polygon
    """
    if not bbox.north_west:
        bbox = bbox2_to_bbox4(bbox)

    sw = (bbox.south_west.longitude, bbox.south_west.latitude)
    se = (bbox.south_east.longitude, bbox.south_east.latitude)
    ne = (bbox.north_east.longitude, bbox.north_east.latitude)
    nw = (bbox.north_west.longitude, bbox.north_west.latitude)

    # Build closed polygon
    polygon = Polygon([sw, se, ne, nw, sw])
    return from_shape(polygon, srid=4326)


### Point utils

def make_point_schema(obj: Union[
    dict,
    PointSchema,
    ShapelyPoint,
    WKBElement,
    object  # for SQLAlchemy ORM row with `.geom`
]) -> PointSchema:

    """
    Convert various point-like inputs into a PointSchema.
    Supported:
      - dict with keys: {"lng", "lat"} or {"longitude", "latitude"}
      - PointSchema
      - shapely.geometry.Point
      - geoalchemy2 WKBElement
      - ORM row with `.geom` attribute (WKBElement or Shapely)
    """

    # Already correct
    if isinstance(obj, PointSchema):
        return obj

    # Dict input
    if isinstance(obj, dict):
        if "lng" in obj and "lat" in obj:
            return PointSchema(latitude=obj["lat"], longitude=obj["lng"])
        elif "longitude" in obj and "latitude" in obj:
            return PointSchema(latitude=obj["latitude"], longitude=obj["longitude"])
        else:
            raise ValueError("Dict must have (lng, lat) or (longitude, latitude) keys")

    # Shapely Point
    if isinstance(obj, ShapelyPoint):
        return PointSchema(latitude=obj.y, longitude=obj.x)

    # PostGIS WKBElement
    if isinstance(obj, WKBElement):
        shp = to_shape(obj)  # convert to Shapely
        return PointSchema(latitude=shp.y, longitude=shp.x)

    # ORM row with .geom
    if hasattr(obj, "geom"):
        geom = obj.geom
        if isinstance(geom, WKBElement):
            shp = to_shape(geom)
            return PointSchema(latitude=shp.y, longitude=shp.x)
        elif isinstance(geom, ShapelyPoint):
            return PointSchema(latitude=geom.y, longitude=geom.x)
        else:
            raise TypeError(f"Unsupported geom type: {type(geom)}")

    # Explicitly reject lists, tuples, or floats (to avoid ambiguity)
    if isinstance(obj, (list, tuple, float, int)):
        raise ValueError("lat/lng is ambiguous, please pass a dict")

    raise TypeError(f"Unsupported type: {type(obj)}")

def point_schema_to_postgis(point: PointSchema, srid: int = 4326) -> WKBElement:
    """
    Convert PointSchema -> PostGIS WKBElement for storage in SQLAlchemy.
    Default SRID = 4326 (WGS84).
    """
    shp = ShapelyPoint(point.longitude, point.latitude)  # Shapely uses (x=lng, y=lat)
    return from_shape(shp, srid=srid)


### Point to BBox
def point_to_bbox(point: PointSchema, size_m: float = 20.0) -> BoundingBox4Point:
    """
    Create a small bounding box (size_m x size_m, centered on point) around a PointSchema.
    Approximates conversion from meters to degrees using WGS84.

    Args:
        point: PointSchema(lat, lng)
        size_m: box width/height in meters (default=20m)

    Returns:
        BoundingBox4Point
    """
    lat = point.latitude
    lng = point.longitude

    # Convert meters to degrees
    delta_lat = size_m / 111_320.0
    delta_lng = size_m / (111_320.0 * math.cos(math.radians(lat)))

    north = lat + delta_lat / 2
    south = lat - delta_lat / 2
    east = lng + delta_lng / 2
    west = lng - delta_lng / 2

    return BoundingBox4Point(
        north_west=PointSchema(latitude=north, longitude=west),
        north_east=PointSchema(latitude=north, longitude=east),
        south_west=PointSchema(latitude=south, longitude=west),
        south_east=PointSchema(latitude=south, longitude=east),
    )
