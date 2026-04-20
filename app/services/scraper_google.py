import httpx
from bs4 import BeautifulSoup
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def scraper_google(query: str = "entreprises Bénin", limit: int = 20) -> list[dict]:
    """
    Extrait des prospects via Google.
    - Si SERP_API_KEY est définie → utilise SerpApi (fiable, recommandé)
    - Sinon → scraping direct Google (pour développement local)
    """
    if settings.SERP_API_KEY:
        logger.info("Google: utilisation de SerpApi.")
        return await _via_serpapi(query, limit)

    logger.info("Google: scraping direct (pas de clé SerpApi).")
    return await _scraping_direct(query, limit)


# ── Mode SerpApi (production) ─────────────────────────────────────────────────

async def _via_serpapi(query: str, limit: int) -> list[dict]:
    """
    SerpApi retourne des résultats Google structurés en JSON.
    Obtenez une clé gratuite sur https://serpapi.com
    """
    params = {
        "engine":  "google",
        "q":       query,
        "api_key": settings.SERP_API_KEY,
        "num":     limit,
        "hl":      "fr",
        "gl":      "bj",   # Bénin
    }
    prospects = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            reponse = await client.get("https://serpapi.com/search", params=params)
            reponse.raise_for_status()
            data = reponse.json()

            for r in data.get("organic_results", [])[:limit]:
                nom = r.get("title", "").split(" - ")[0].strip()
                if nom:
                    prospects.append({
                        "nom":         nom,
                        "secteur":     None,
                        "ville":       "Bénin",
                        "telephone":   None,
                        "description": r.get("snippet", "")[:500],
                        "source":      "google",
                    })
        except httpx.HTTPStatusError as e:
            logger.error(f"SerpApi HTTP {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"SerpApi erreur: {e}")

    logger.info(f"Google (SerpApi): {len(prospects)} prospects extraits.")
    return prospects


# ── Mode scraping direct (développement) ─────────────────────────────────────

async def _scraping_direct(query: str, limit: int) -> list[dict]:
    """
    Scraping direct de Google.
    Note : Google peut bloquer les robots — utilisez SerpApi en production.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9",
    }
    # Formater la requête pour cibler le Bénin
    query_complete = f"{query} Cotonou Bénin"
    url = f"https://www.google.com/search?q={query_complete}&num={limit}&hl=fr"
    prospects = []

    async with httpx.AsyncClient(headers=headers, timeout=30, follow_redirects=True) as client:
        try:
            reponse = await client.get(url)
            reponse.raise_for_status()

            soup = BeautifulSoup(reponse.text, "html.parser")

            # Résultats organiques Google
            resultats = soup.select("div.g") or soup.select("div[data-hveid]")

            for r in resultats[:limit]:
                titre_el   = r.select_one("h3")
                snippet_el = (
                    r.select_one(".VwiC3b") or
                    r.select_one(".IsZvec") or
                    r.select_one("span[class*='snippet']")
                )

                nom = titre_el.get_text(strip=True) if titre_el else None
                description = snippet_el.get_text(strip=True)[:500] if snippet_el else None

                if nom and len(nom) > 3:
                    # Nettoyer le titre : enlever " - Wikipedia", " | Site officiel", etc.
                    nom = nom.split(" - ")[0].split(" | ")[0].strip()
                    prospects.append({
                        "nom":         nom,
                        "secteur":     None,
                        "ville":       "Bénin",
                        "telephone":   None,
                        "description": description,
                        "source":      "google",
                    })

        except httpx.HTTPStatusError as e:
            logger.error(f"Google scraping HTTP {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Google scraping erreur: {e}")

    logger.info(f"Google (direct): {len(prospects)} prospects extraits.")
    return prospects
