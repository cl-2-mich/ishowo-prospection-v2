import logging
from sqlalchemy.orm import Session

from app.services.scraper_goafrica import scraper_goafrica
from app.services.scraper_google import scraper_google
from app.repository.prospect_repository import ProspectRepository
from app.schemas.prospect import ProspectCreate

logger = logging.getLogger(__name__)


class CollectService:
    """
    Service Layer — Phase 1 : Collecte & stockage des données brutes.

    Responsabilités :
    1. Appeler les scrapers selon les sources demandées
    2. Valider chaque donnée brute via Pydantic (ProspectCreate)
    3. Insérer en BDD en évitant les doublons (via le Repository)
    4. Retourner un rapport de collecte
    """

    def __init__(self, db: Session):
        self.db   = db
        self.repo = ProspectRepository(db)

    async def collecter(
        self,
        query:   str,
        sources: list[str],
        limit:   int,
    ) -> dict:
        """
        Lance le scraping depuis les sources sélectionnées
        et stocke les données brutes en MySQL.
        """
        toutes_donnees_brutes: list[dict] = []

        # ── 1. Collecte depuis les sources ───────────────────────────────────
        if "goafrica" in sources:
            logger.info("Lancement du scraper GoAfrica...")
            donnees = await scraper_goafrica(limit=limit)
            toutes_donnees_brutes.extend(donnees)
            logger.info(f"GoAfrica: {len(donnees)} entrées collectées.")

        if "google" in sources:
            logger.info(f"Lancement du scraper Google (query='{query}')...")
            donnees = await scraper_google(query=query, limit=limit)
            toutes_donnees_brutes.extend(donnees)
            logger.info(f"Google: {len(donnees)} entrées collectées.")

        # ── 2. Validation + insertion ─────────────────────────────────────────
        inseres  = 0
        doublons = 0
        erreurs  = 0

        for brut in toutes_donnees_brutes:
            try:
                # Pydantic valide et normalise (téléphone, nom, etc.)
                schema = ProspectCreate(**brut)

                # Le repository gère le dédoublonnage
                resultat = self.repo.creer(schema)

                if resultat:
                    inseres += 1
                    logger.debug(f"Inséré : {resultat.nom}")
                else:
                    doublons += 1
                    logger.debug(f"Doublon ignoré : {brut.get('nom')}")

            except Exception as e:
                erreurs += 1
                logger.warning(f"Données invalides ignorées: {e} | Data: {brut}")

        # ── 3. Rapport ────────────────────────────────────────────────────────
        logger.info(
            f"Collecte terminée → collectés: {len(toutes_donnees_brutes)}, "
            f"insérés: {inseres}, doublons: {doublons}, erreurs: {erreurs}"
        )

        return {
            "total_collectes": len(toutes_donnees_brutes),
            "total_inseres":   inseres,
            "total_doublons":  doublons,
            "message": (
                f"✅ Collecte terminée depuis {', '.join(sources)}. "
                f"{inseres} nouveau(x) prospect(s) enregistré(s)."
            ),
        }
