from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.models.prospect import Prospect, ProspectStatus
from app.schemas.prospect import ProspectCreate


class ProspectRepository:
    """
    Pattern Repository : toute interaction avec la BDD passe ici.
    Les services ne font JAMAIS de requêtes SQL directement.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Lecture ──────────────────────────────────────────────────────────────

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[str] = None,
    ) -> list[Prospect]:
        query = self.db.query(Prospect)
        if statut:
            query = query.filter(Prospect.statut == statut)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, prospect_id: int) -> Optional[Prospect]:
        return self.db.query(Prospect).filter(Prospect.id == prospect_id).first()

    def get_non_traites(self) -> list[Prospect]:
        """Retourne les prospects en statut RAW (pas encore analysés)."""
        return (
            self.db.query(Prospect)
            .filter(Prospect.statut == ProspectStatus.RAW)
            .all()
        )

    # ── Vérifications dédoublonnage ──────────────────────────────────────────

    def existe_par_telephone(self, telephone: str) -> bool:
        return (
            self.db.query(Prospect)
            .filter(Prospect.telephone == telephone)
            .first() is not None
        )

    def existe_par_nom(self, nom: str) -> bool:
        return (
            self.db.query(Prospect)
            .filter(Prospect.nom == nom)
            .first() is not None
        )

    # ── Écriture ─────────────────────────────────────────────────────────────

    def creer(self, data: ProspectCreate) -> Optional[Prospect]:
        """
        Insère un nouveau prospect en base.
        Retourne None si doublon détecté (téléphone ou nom identique).
        """
        # Dédoublonnage par téléphone (champ unique en BDD)
        if data.telephone and self.existe_par_telephone(data.telephone):
            return None

        # Dédoublonnage par nom (évite les entreprises sans téléphone en double)
        if self.existe_par_nom(data.nom):
            return None

        prospect = Prospect(**data.model_dump())
        try:
            self.db.add(prospect)
            self.db.commit()
            self.db.refresh(prospect)
            return prospect
        except IntegrityError:
            self.db.rollback()
            return None

    def compter(self) -> int:
        return self.db.query(Prospect).count()
    def update(self, prospect_id: int, data) -> Optional[Prospect]:
        prospect = self.get_by_id(prospect_id)
        if not prospect:
            return None
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(prospect, field, value)
        self.db.commit()
        self.db.refresh(prospect)
        return prospect