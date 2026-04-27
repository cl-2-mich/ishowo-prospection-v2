import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def scraper_google(query: str = "entreprises Bénin", limit: int = 20) -> list[dict]:
    if settings.SERP_API_KEY:
        return await _via_serpapi(query, limit)
    return []


async def _via_serpapi(query: str, limit: int) -> list[dict]:
    params = {
        "engine":  "google",
        "q":       query,
        "api_key": settings.SERP_API_KEY,
        "num":     limit,
        "hl":      "fr",
        "gl":      "bj",
    }
    prospects = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            reponse = await client.get(
                "https://serpapi.com/search.json",
                params=params
            )
            reponse.raise_for_status()
            data = reponse.json()
            logger.info(f"SerpApi: {len(data.get('organic_results', []))} résultats")

            for r in data.get("organic_results", [])[:limit]:
                nom = r.get("title", "").split(" - ")[0].split(" | ")[0].strip()
                if nom and len(nom) > 3:
                    prospects.append({
                        "nom":         nom,
                        "secteur":     None,
                        "ville":       "Bénin",
                        "telephone":   None,
                        "description": r.get("snippet", "")[:500],
                        "source":      "google",
                    })
        except Exception as e:
            logger.error(f"SerpApi erreur: {e}")

    logger.info(f"Google (SerpApi): {len(prospects)} prospects extraits.")
    return prospects