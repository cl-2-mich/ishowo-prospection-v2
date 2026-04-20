import logging
from sqlalchemy.orm import Session
from app.services.ai_service import analyser_prospect
from app.repository.prospect_repository import ProspectRepository
from app.schemas.prospect import ProspectUpdate
from app.models.prospect import ProspectStatus

logger = logging.getLogger(__name__)


class ProcessService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProspectRepository(db)

    async def traiter(self) -> dict:
        prospects = self.repo.get_non_traites()

        if not prospects:
            return {
                "total_processed": 0,
                "message": "Aucun prospect en attente de traitement.",
            }

        traites = 0
        for prospect in prospects:
            try:
                analyse = await analyser_prospect(
                    nom=prospect.nom,
                    secteur=prospect.secteur,
                    ville=prospect.ville,
                    description=prospect.description,
                )
                update = ProspectUpdate(
                    categorie=analyse.get("categorie"),
                    score_ia=str(analyse.get("score", 0)),
                    pertinence_ishowo=analyse.get("pertinence_ishowo"),
                    justification_ia=analyse.get("justification"),
                    statut=ProspectStatus.SCORED,
                )
                self.repo.update(prospect.id, update)
                traites += 1
                logger.info(f"✅ {prospect.nom} → score {analyse.get('score')}/10")

            except Exception as e:
                logger.error(f"❌ Erreur {prospect.nom}: {e}")
                self.repo.update(
                    prospect.id,
                    ProspectUpdate(statut=ProspectStatus.PROCESSED),
                )

        return {
            "total_processed": traites,
            "message": f"{traites} prospect(s) analysé(s) et scoré(s) par l'IA.",
        }