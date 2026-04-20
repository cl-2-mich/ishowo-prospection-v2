import httpx
from bs4 import BeautifulSoup
from typing import Optional
import logging

logger = logging.getLogger(__name__)

BASE_URL   = "https://www.goafricaonline.com"
# Page des annuaires d'entreprises au Bénin
ANNUAIRE_URL = f"{BASE_URL}/bj/annuaires"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def scraper_goafrica(limit: int = 20) -> list[dict]:
    """
    Scrape les entreprises béninoises sur Go Africa Online.
    Retourne une liste de dicts bruts (non validés).
    """
    prospects = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30,
        follow_redirects=True,
    ) as client:
        # ── Page 1 de l'annuaire ─────────────────────────────
        try:
            reponse = await client.get(ANNUAIRE_URL)
            reponse.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"GoAfrica HTTP {e.response.status_code}: {e}")
            return []
        except httpx.RequestError as e:
            logger.error(f"GoAfrica connexion impossible: {e}")
            return []

        soup = BeautifulSoup(reponse.text, "html.parser")

        # ── Extraction des cartes entreprises ────────────────
        # GoAfrica utilise des balises article ou div avec classe "company"
        cartes = (
            soup.select("article.company-item") or
            soup.select("div.company-item") or
            soup.select(".listing-item") or
            soup.select("div[class*='company']") or
            soup.select("li[class*='company']")
        )

        logger.info(f"GoAfrica: {len(cartes)} cartes trouvées sur la page.")

        for carte in cartes[:limit]:
            data = _extraire_carte(carte)
            if data and data.get("nom"):
                prospects.append(data)

        # ── Si aucune carte trouvée, scraping alternatif ─────
        if not prospects:
            prospects = _extraction_alternative(soup, limit)

    logger.info(f"GoAfrica: {len(prospects)} prospects extraits au total.")
    return prospects


def _extraire_carte(carte: BeautifulSoup) -> Optional[dict]:
    """Parse les informations d'une carte entreprise."""
    try:
        # Nom de l'entreprise
        nom_el = (
            carte.select_one("h2.company-name") or
            carte.select_one("h3.company-name") or
            carte.select_one(".title") or
            carte.select_one("h2") or
            carte.select_one("h3") or
            carte.select_one("a[class*='name']")
        )
        nom = nom_el.get_text(strip=True) if nom_el else None
        if not nom:
            return None

        # Secteur d'activité
        secteur_el = (
            carte.select_one(".category") or
            carte.select_one(".secteur") or
            carte.select_one(".activity") or
            carte.select_one("span[class*='cat']") or
            carte.select_one("[class*='sector']")
        )
        secteur = secteur_el.get_text(strip=True) if secteur_el else None

        # Ville
        ville_el = (
            carte.select_one(".city") or
            carte.select_one(".location") or
            carte.select_one(".ville") or
            carte.select_one("span[class*='loc']") or
            carte.select_one("[class*='address']")
        )
        ville = ville_el.get_text(strip=True) if ville_el else "Bénin"

        # Téléphone
        tel_el = (
            carte.select_one("a[href^='tel:']") or
            carte.select_one(".phone") or
            carte.select_one(".tel")
        )
        telephone = None
        if tel_el:
            telephone = (
                tel_el.get("href", "").replace("tel:", "").strip() or
                tel_el.get_text(strip=True)
            )

        # Description
        desc_el = (
            carte.select_one(".description") or
            carte.select_one(".excerpt") or
            carte.select_one("p")
        )
        description = desc_el.get_text(strip=True)[:500] if desc_el else None

        return {
            "nom":         nom,
            "secteur":     secteur,
            "ville":       ville,
            "telephone":   telephone,
            "description": description,
            "source":      "goafrica",
        }
    except Exception as e:
        logger.warning(f"Erreur parsing carte: {e}")
        return None


def _extraction_alternative(soup: BeautifulSoup, limit: int) -> list[dict]:
    """
    Fallback si les sélecteurs principaux ne trouvent rien.
    Extrait tous les liens d'entreprises de la page.
    """
    logger.warning("GoAfrica: sélecteurs principaux inefficaces, passage en mode alternatif.")
    prospects = []
    liens = soup.select("a[href*='/bj/']")[:limit]

    for lien in liens:
        nom = lien.get_text(strip=True)
        if nom and len(nom) > 3:
            prospects.append({
                "nom":         nom,
                "secteur":     None,
                "ville":       "Bénin",
                "telephone":   None,
                "description": None,
                "source":      "goafrica",
            })

    return prospects
