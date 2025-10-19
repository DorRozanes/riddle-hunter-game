from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Enemy

def purge_old_enemies(db: Session):
    """
    Delete all enemies whose spawn_time is older than 24 hours.
    """
    cutoff = datetime.utcnow() - timedelta(hours=24)

    deleted_count = (
        db.query(Enemy)
        .filter(Enemy.spawn_time < cutoff)
        .delete(synchronize_session=False)
    )

    db.commit()
    return deleted_count