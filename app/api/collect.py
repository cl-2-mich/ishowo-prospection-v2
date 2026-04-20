from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.collect_service import CollectService
from app.schemas.prospect import CollectRequest, CollectResponse

router = APIRouter()


@router.post(
    "/collect",
    response_model=CollectResponse,
    status_code=status.HTTP_200_OK,
    summary="🔍 Lance la collecte de prospects",
    description="""
**Phase 1 — Collecte de données**

Lance le scraping depuis les sources sélectionnées (Go Africa Online, Google),
normalise les données et les stocke en base MySQL.

**Sources disponibles :**
- `goafrica` : Annuaire d'entreprises béninoises sur Go Africa Online
- `google` : Résultats Google (nécessite une clé SerpApi pour la production)

**Traitement automatique :**
- Normalisation des numéros de téléphone (+229 XX XX XX XX)
- Dédoublonnage par téléphone et par nom
- Validation des données via Pydantic
    """,
)
async def collecter_prospects(
    body: CollectRequest,
    db: Session = Depends(get_db),
):
    """
    Lance le pipeline de collecte.

    - **query** : Requête de recherche Google (ex: "pharmacies Cotonou")
    - **sources** : Liste des sources à scraper ["goafrica", "google"]
    - **limit** : Nombre maximum de prospects par source
    """
    # Validation des sources
    sources_valides = {"goafrica", "google"}
    sources_invalides = set(body.sources) - sources_valides
    if sources_invalides:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Sources invalides : {sources_invalides}. "
                   f"Sources acceptées : {sources_valides}",
        )

    if not body.sources:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Au moins une source doit être sélectionnée.",
        )

    try:
        service = CollectService(db)
        resultat = await service.collecter(
            query=body.query,
            sources=body.sources,
            limit=body.limit,
        )
        return resultat

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la collecte : {str(e)}",
        )
