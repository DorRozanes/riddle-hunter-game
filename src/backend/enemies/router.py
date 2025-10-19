from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from shapely import wkb

from dependencies import get_db
from dependencies import get_current_user
from models import User, Enemy, Place
from schemas.basic_location import PointSchema, PlaceSchema
from enemies.enemy_schemas import EnemySchema, EnemyDetailSchema, EnemyDefeatRequest, EnemyDefeatResponse
from enemies.services.purge_enemies import purge_old_enemies
from enemies.services.spawn_enemies_service import spawn_enemies
from enemies.services.general_riddles import check_answer

router = APIRouter(prefix="/api/enemies", tags=["enemies"])

@router.post("/spawn", response_model=List[EnemySchema])
def spawn_for_player(
    player_location: PointSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    First, purges old enemies
    Spawns enemies around the current player’s location.
    Returns list of active enemies (without riddle/answer).
    """

    purge_old_enemies(db)

    # 1️⃣ Query nearby places within 400m radius
    # Assuming Place has a bounding_box (Polygon)
    nearby_places = (
        db.query(Place)
        .filter(
            Place.bounding_box.ST_DWithin(
                f"SRID=4326;POINT({player_location.longitude} {player_location.latitude})",
                0.004  # ~400m in degrees (rough)
            )
        )
        .all()
    )

    if not nearby_places:
        raise HTTPException(status_code=404, detail="No nearby places found")

    # 2️⃣ Spawn enemies
    spawned_enemies = spawn_enemies(
        db=db,
        player=current_user,
        nearby_places=nearby_places,
        max_enemies=10,
        radius_m=400,
        min_distance_m=40,
        lifespan_hours=2,
    )

    # 3️⃣ Return active enemies (without riddle/answer)
    return_enemies = []
    for e in spawned_enemies:
        e_loc = wkb.loads(bytes(e.location.data))
        return_enemies.append(EnemySchema(
            id=e.id,
            enemy_type=e.enemy_type,
            location=PointSchema(latitude=e_loc.y, longitude=e_loc.x),
            expires_at=e.expires_at,
            defeated=e.defeated,
        ))
    return return_enemies


@router.get("/", response_model=List[EnemySchema])
def list_active_enemies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all active enemies for current player.
    """
    active_enemies = db.query(Enemy).filter(Enemy.user_id == current_user.user_id).filter(Enemy.expires_at > datetime.utcnow()).all()
    return_enemies = []
    for e in active_enemies:
        e_loc = wkb.loads(bytes(e.location.data))
        return_enemies.append(EnemySchema(
            id=e.id,
            enemy_type=e.enemy_type,
            location=PointSchema(latitude=e_loc.y, longitude=e_loc.x),
            expires_at=e.expires_at,
            defeated=e.defeated,
        ))
    return return_enemies

@router.get("/{enemy_id}/riddle", response_model=EnemyDetailSchema)
def get_enemy_riddle(
    enemy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enemy = (
        db.query(Enemy)
        .filter(Enemy.id == enemy_id, Enemy.user_id == current_user.user_id)
        .first()
    )
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")

    e_loc = wkb.loads(bytes(enemy.location.data))
    return EnemyDetailSchema(
        id=enemy.id,
        enemy_type=enemy.enemy_type,
        location=PointSchema(latitude=e_loc.y, longitude=e_loc.x),
        expires_at=enemy.expires_at,
        defeated=enemy.defeated,
        riddle=enemy.riddle,
    )

@router.post("/{enemy_id}/defeat", response_model=EnemyDefeatResponse)
def defeat_enemy(
    enemy_id: int,
    req: EnemyDefeatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Player attempts to solve an enemy's riddle.
    """
    enemy = (
        db.query(Enemy)
        .filter(Enemy.id == enemy_id, Enemy.user_id == current_user.user_id)
        .first()
    )
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")

    if enemy.defeated:
        raise HTTPException(status_code=400, detail="Enemy already defeated")

    # Check answer
    if not check_answer(req.answer, enemy.answer):
        return EnemyDefeatResponse(success=False, message="Wrong answer!")

    # ✅ Defeat enemy
    enemy.defeated = 1
    db.add(enemy)

    # Award points
    current_user.xp_points += 1
    db.add(current_user)
    db.commit()
    db.refresh(enemy)
    db.refresh(current_user)

    return EnemyDefeatResponse(
        success=True,
        message=f"You defeated the {enemy.enemy_type}!",
        new_score=current_user.xp_points,
    )
