from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# DB_URI = "postgresql+psycopg://postgres:postgres@fastapi-db/fastapi?application_name=fastapi-psycopg"

naming_convention = {
    "pk": "pk_%(table_name)s",  # Primary key constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign key constraint
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique constraint
    "ix": "ix_%(table_name)s_%(column_0_name)s",  # Index
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check constraint
}

# Create MetaData with the naming convention
metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)


DB_URI = str(settings.db_uri)
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Function to get a DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
