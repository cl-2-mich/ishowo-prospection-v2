# ISHOWO — Phase 1 : Collecte de données

## Installation en 5 étapes

```bash
# 1. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la base de données
cp .env.example .env
# → Ouvrez .env et mettez votre mot de passe MySQL

# 4. Créer la base MySQL
mysql -u root -p < database.sql

# 5. Lancer l'API
uvicorn app.main:app --reload
```

## Tester rapidement (sans scraper le web)

```bash
python seed.py   # Injecte 8 prospects béninois fictifs
```

## Tester les endpoints

Ouvrez http://localhost:8000/docs

### POST /collect
```json
{
  "query": "pharmacies Cotonou Bénin",
  "sources": ["goafrica", "google"],
  "limit": 20
}
```

### GET /prospects
```
http://localhost:8000/prospects?statut=raw&limit=50
```

### GET /prospects/stats
```
http://localhost:8000/prospects/stats
```
