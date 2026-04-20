from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.repository.prospect_repository import ProspectRepository
from app.schemas.prospect import ProspectResponse

router = APIRouter()


@router.get(
    "/prospects",
    response_model=list[ProspectResponse],
    summary="📋 Liste les prospects collectés",
    description="""
Retourne tous les prospects stockés en base, filtrables par statut.

**Statuts disponibles :**
- `raw` : Collectés mais pas encore analysés par l'IA
- `processed` : Normalisés
- `scored` : Analysés et scorés par l'IA (Phase 2)
    """,
)
def lister_prospects(
    skip:   int            = Query(0,    ge=0,  description="Offset de pagination"),
    limit:  int            = Query(50,   ge=1,  le=200, description="Nombre max de résultats"),
    statut: Optional[str]  = Query(None, description="Filtrer par statut (raw, processed, scored)"),
    db:     Session        = Depends(get_db),
):
    repo = ProspectRepository(db)
    return repo.get_all(skip=skip, limit=limit, statut=statut)


@router.get(
    "/prospects/stats",
    summary="📊 Statistiques de la base de prospects",
)
def stats_prospects(db: Session = Depends(get_db)):
    repo = ProspectRepository(db)
    total = repo.compter()
    raw = len(repo.get_non_traites())
    return {
        "total":         total,
        "en_attente_ia": raw,
        "traites":       total - raw,
    }
