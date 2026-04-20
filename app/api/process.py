from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.process_service import ProcessService

router = APIRouter()


@router.post(
    "/process",
    status_code=status.HTTP_200_OK,
    summary="🤖 Analyse les prospects avec l'IA (Ollama Llama 3.2)",
)
async def traiter_prospects(db: Session = Depends(get_db)):
    """
    Phase 2 — Lance l'analyse IA sur tous les prospects en statut RAW.
    Chaque prospect reçoit une catégorie, un score (0-10) et une justification.
    """
    try:
        service = ProcessService(db)
        result = await service.traiter()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement : {str(e)}",
        )