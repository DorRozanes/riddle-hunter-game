import requests
import os
from ..schemas.basic_location import PointSchema

GOOGLE_API_KEY = os.getenv("google_api_key")

def find_location_info_from_google(point: PointSchema) -> dict | None:
    """
    Query Google Places Nearby Search for a point.
    Try radii 1m, 20m, 50m until we find a non-route result.
    Returns the first valid result or None.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    radii = [1, 20, 50]

    for radius in radii:
        params = {
            "location": f"{point.latitude},{point.longitude}",
            "radius": radius,
            "key": GOOGLE_API_KEY,
        }

        r = requests.get(url, params=params).json()
        results = r.get("results", [])
        if not results:
            continue

        print ("--------> Debug. All results:")
        print(results)

        return results