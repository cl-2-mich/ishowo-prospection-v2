from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # vérifie la connexion avant chaque requête
    pool_recycle=3600,    # recycle les connexions toutes les heures
    echo=False,           # mettre True pour voir les requêtes SQL en debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency FastAPI — injecte une session DB dans chaque route.
    La session est fermée automatiquement après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
