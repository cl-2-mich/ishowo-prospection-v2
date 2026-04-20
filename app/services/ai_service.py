import ollama
import json
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Tu es un expert en analyse commerciale pour la solution ISHOWO — un logiciel de gestion
de stock et de caisse pour les entreprises d'Afrique de l'Ouest.

Ton rôle est d'analyser des prospects (entreprises locales) et de les qualifier selon
leur potentiel de conversion pour ISHOWO.

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après.
"""

ANALYSIS_PROMPT = """
Analyse cette entreprise et retourne un JSON avec cette structure exacte :
{{
  "categorie": "commerce" ou "pharmacie" ou "service" ou "autre",
  "pertinence_ishowo": "oui" ou "non",
  "score": un nombre entier entre 0 et 10,
  "justification": "une phrase courte"
}}

Entreprise :
- Nom : {nom}
- Secteur : {secteur}
- Ville : {ville}
- Description : {description}

Critères :
- 8-10 : Fort besoin de stock (pharmacie, épicerie, quincaillerie, supermarché)
- 5-7  : Besoin modéré (restaurant, boutique, magasin)
- 0-4  : Peu de besoin (service pur, cabinet, ONG)
"""


async def analyser_prospect(
    nom: str,
    secteur: str | None,
    ville: str | None,
    description: str | None,
) -> dict:
    prompt = ANALYSIS_PROMPT.format(
        nom=nom,
        secteur=secteur or "Non précisé",
        ville=ville or "Non précisée",
        description=description or "Aucune description",
    )
    try:
        response = await asyncio.to_thread(_appeler_ollama, prompt)
        return response
    except Exception as e:
        logger.error(f"Erreur Ollama pour '{nom}': {e}")
        return _scoring_fallback(secteur, description)


def _appeler_ollama(prompt: str) -> dict:
    client = ollama.Client(host=settings.OLLAMA_HOST)
    response = client.chat(
        model=settings.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.1},
    )
    content = response["message"]["content"].strip()
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)


def _scoring_fallback(secteur: str | None, description: str | None) -> dict:
    keywords_high = ["pharmacie", "épicerie", "supermarché", "quincaillerie", "stock"]
    keywords_mid = ["restaurant", "boutique", "commerce", "magasin"]
    text = f"{secteur or ''} {description or ''}".lower()

    if any(kw in text for kw in keywords_high):
        return {"categorie": "commerce", "pertinence_ishowo": "oui",
                "score": 8, "justification": "Fort besoin de gestion de stock détecté."}
    elif any(kw in text for kw in keywords_mid):
        return {"categorie": "commerce", "pertinence_ishowo": "oui",
                "score": 5, "justification": "Besoin modéré de gestion de stock."}
    return {"categorie": "service", "pertinence_ishowo": "non",
            "score": 2, "justification": "Peu de besoin en gestion de stock."}