from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings
from alembic.runtime.migration import MigrationContext
from alembic.autogenerate.api import AutogenContext, compare_metadata

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_postgis(engine):
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
        conn.commit()

def check_schema_sync(engine, metadata):
    """
    Detects if the actual DB schema differs from SQLAlchemy models.
    Ignores PostGIS tables (they are not defined in SQLAlchemy models).
    Returns True if everything is in sync, False otherwise.
    """

    with engine.connect() as conn:
        context = MigrationContext.configure(conn)

        def include_object(obj, name, type_, reflected, compare_to):
            if type_ == "table" and name in {
                "spatial_ref_sys",
                "geometry_columns",
                "topology",
                "layer",
            }:
                return False
            return True

        # Pass it as an option to MigrationContext
        context = MigrationContext.configure(
            connection=conn,
            opts={"include_object": include_object}
        )

        # Now run the comparison
        diff = compare_metadata(context, metadata)

    if not diff:
        print("✅ Database schema is up to date with SQLAlchemy models.")
        return True
    else:
        print("⚠️ Schema differences detected between DB and models:")
        for d in diff:
            print("  •", d)
        print("Consider running: alembic revision --autogenerate -m 'sync' && alembic upgrade head")
        return False