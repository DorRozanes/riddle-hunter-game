import random
from datetime import datetime, timedelta
from shapely.geometry import shape, Point
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session
from shapely import wkb

from models import Enemy
from enums.type_priority import TYPE_PRIORITY
from enemies.enums.type_locations_for_enemies import PLACE_TYPES
from enemies.services.general_riddles import get_riddle


def get_enemy_type_for_place(place_type: str):
    for entry in PLACE_TYPES:
        if entry["place_type"] == place_type:
            return entry["enemy_type"]



def spawn_enemies(
    db: Session,
    player,
    nearby_places: list,
    max_enemies: int = 10,
    radius_m: int = 400,
    min_distance_m: int = 40,
    lifespan_hours: int = 2,
):
    """
    Spawn enemies for player:
    - One per place, up to max_enemies
    - Prioritized by TYPE_PRIORITY
    - ≥ min_distance_m apart
    """

    # Already existing enemies for this player (to avoid duplicates)
    existing = (
        db.query(Enemy)
        .filter(Enemy.user_id == player.user_id)
        .filter(Enemy.expires_at > datetime.utcnow())
        .filter(Enemy.defeated == 0)
        .all()
    )

    existing_enemies = [wkb.loads(bytes(e.location.data)) for e in existing]

    # Sort places by TYPE_PRIORITY (lower number = higher priority)
    TYPE_PRIORITY_RANK = {t: i for i, t in enumerate(TYPE_PRIORITY)}

    def place_priority(place):
        if not place.place_types:
            return len(TYPE_PRIORITY_RANK)
        # Find the best (lowest index) among its types
        return min(
            TYPE_PRIORITY_RANK.get(t, len(TYPE_PRIORITY_RANK))
            for t in place.place_types
        )

    sorted_places = sorted(nearby_places, key=place_priority)

    spawned = []
    for place in sorted_places:
        print ("-----> Debug: going over places. Enemies spawned: ", spawned," Max enemies: ", max_enemies)
        if len(spawned+existing_enemies) >= max_enemies:
            break

        place_type = TYPE_PRIORITY[place_priority(place)]

        # Match place_type → enemy_type
        enemy_type = get_enemy_type_for_place(place_type)
        if not enemy_type:
            continue  # skip if no mapping exists

        print("-------> Debug: Enemy type: ",enemy_type)

        # Pick a random point inside place's geometry
        geom = to_shape(place.bounding_box)  # polygon from DB
        if not geom.is_valid or geom.is_empty:
            continue

        # crude rejection-sampling: try random points in bbox until inside
        minx, miny, maxx, maxy = geom.bounds
        for _ in range(20):
            rand_point = Point(
                random.uniform(minx, maxx),
                random.uniform(miny, maxy),
            )
            if geom.contains(rand_point):
                # Ensure distance ≥ min_distance_m
                # Convert 'spawned' locations to Shapely geometries
                spawned_points = [wkb.loads(bytes(e.location.data)) for e in spawned]

                # Combine all points
                comparison_points = existing_enemies + spawned_points

                # Compute distances (in meters)
                distances_m = [rand_point.distance(ep) * 111_000 for ep in comparison_points]

                # Check if all distances are above the threshold
                if all(d >= min_distance_m for d in distances_m):
                    new_riddle = get_riddle(place_type)

                    enemy = Enemy(
                        enemy_type=enemy_type,
                        location=from_shape(rand_point, srid=4326),
                        riddle = new_riddle["riddle"],
                        answer = new_riddle["answer"],
                        expires_at=datetime.utcnow() + timedelta(hours=lifespan_hours),
                        user_id=player.user_id,
                    )
                    db.add(enemy)
                    db.flush()  # get ID before refresh
                    spawned.append(enemy)
                    break

    db.commit()
    for e in spawned:
        db.refresh(e)

    return spawned
