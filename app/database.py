from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./chat.db"  # Pode trocar para PostgreSQL, MySQL etc.

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  #necessário para SQLite
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency para endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
