## 🔍 ISHOWO Prospection v2

Système de prospection automatique basé sur la collecte de données web et l'analyse IA (Ollama Llama 3.2).

## 📋 Description

Ce projet permet de :
1. **Collecter** des prospects (entreprises, pharmacies, commerces…) depuis le web via des sources comme Google et GoAfrica
2. **Analyser** automatiquement ces prospects avec l'IA pour les scorer et les catégoriser

---

## ⚙️ Installation

### Prérequis

- Python 3.11+
- MySQL
- Ollama avec le modèle Llama 3.2

### Configuration

Copier le fichier `.env.example` en `.env` et remplir les valeurs :

```env
DATABASE_URL=mysql+pymysql://root:votre_mot_de_passe@localhost:3306/ishowo_prospects
SERP_API_KEY=votre_clé_api
APP_ENV=development
```

### Lancer le serveur

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 🚀 API Endpoints

### POST /collect

Lance la collecte de prospects depuis les sources web.

**Body JSON :**
```json
{
  "query": "pharmacies Cotonou Bénin",
  "sources": ["goafrica", "google"],
  "limit": 20
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `query` | string | Terme de recherche |
| `sources` | array | Sources à utiliser (`goafrica`, `google`) |
| `limit` | integer | Nombre maximum de résultats |

**Réponse (200 OK) :**
```json
{
  "message": "Collecte terminée",
  "collected": 18
}
```

---

### POST /process

Lance l'analyse IA (Ollama Llama 3.2) sur tous les prospects en statut `RAW`.

Chaque prospect reçoit automatiquement :
- Une **catégorie**
- Un **score** (0 à 10)
- Une **justification**

> ⚠️ Ce endpoint correspond à la **Phase 2** du pipeline. Il doit être appelé **après** `POST /collect`.

**Requête :** Aucun body requis

```
POST http://localhost:8000/process
```

**Réponse (200 OK) :**
```json
{
  "message": "Traitement terminé",
  "processed": 42
}
```

| Code | Description |
|------|-------------|
| 200 | Traitement effectué avec succès |
| 500 | Erreur lors du traitement (ex: Ollama non disponible) |

---

### GET /prospects

Récupère la liste des prospects collectés.

```
GET http://localhost:8000/prospects?statut=raw&limit=50
```

| Paramètre | Type | Description |
|-----------|------|-------------|
| `statut` | string | Filtrer par statut (`raw`, `processed`) |
| `limit` | integer | Nombre maximum de résultats |

---

## 🔄 Pipeline complet

```
POST /collect  →  POST /process  →  GET /prospects
   (Phase 1)          (Phase 2)        (Consultation)
```

1. Lancer `/collect` pour récupérer des prospects bruts
2. Lancer `/process` pour analyser et scorer les prospects avec l'IA
3. Consulter les résultats via `/prospects`

---

## 🛠️ Stack technique

- **FastAPI** — Framework API
- **SQLAlchemy** — ORM base de données
- **MySQL** — Base de données
- **Ollama Llama 3.2** — Analyse IA des prospects
- **SerpAPI / GoAfrica** — Sources de collecte web

## 🎬 Vidéo de démonstration

[Démonstration ISHOWO](https://www.loom.com/share/15aa6a6de0a842a7aca477c91c59bd71)

> Démonstration complète des 3 endpoints via Swagger UI :
> POST /collect → POST /process → GET /prospects