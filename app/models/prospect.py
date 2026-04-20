from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.database.session import Base
import enum


class ProspectStatus(str, enum.Enum):
    RAW       = "RAW"
    PROCESSED = "PROCESSED"
    SCORED    = "SCORED"

class Prospect(Base):
    __tablename__ = "prospects"

    # ── Identifiant ─────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Données collectées (Phase 1) ─────────────────────────
    nom         = Column(String(255), nullable=False)
    secteur     = Column(String(255), nullable=True)
    ville       = Column(String(100), nullable=True)
    telephone   = Column(String(30),  nullable=True, unique=True)
    description = Column(Text,        nullable=True)
    source      = Column(String(100), nullable=True)   # "goafrica" | "google"

    # ── Champs IA (remplis en Phase 2 par Ollama) ────────────
    categorie           = Column(String(100), nullable=True)
    score_ia            = Column(String(10),  nullable=True)   # "0" à "10"
    pertinence_ishowo   = Column(String(10),  nullable=True)   # "oui" | "non"
    justification_ia    = Column(Text,        nullable=True)

    # ── Statut du pipeline ───────────────────────────────────
    statut = Column(
        Enum(ProspectStatus),
        default=ProspectStatus.RAW,
        nullable=False,
    )

    # ── Horodatage ───────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Prospect id={self.id} nom={self.nom!r} source={self.source}>"
