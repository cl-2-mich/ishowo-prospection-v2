from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.database.session import engine, Base
from app.api import collect, prospects, process

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan : actions au démarrage et à l'arrêt ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Créer les tables MySQL si elles n'existent pas encore
    logger.info("Création des tables MySQL (si nécessaire)...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Base de données prête.")
    yield
    logger.info("Arrêt de l'application.")


# ── Application FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="ISHOWO — Système de Prospection Intelligente",
    description="""
## Phase 1 : Collecte de données

Pipeline de Lead Generation automatisé pour la solution **ISHOWO**.

### Endpoints disponibles :
- `POST /collect` → Lance le scraping (GoAfrica + Google)
- `GET /prospects` → Consulte les prospects collectés
- `GET /prospects/stats` → Statistiques de la base
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Enregistrement des routes ─────────────────────────────────────────────────
app.include_router(collect.router,   tags=["🔍 Phase 1 — Collecte"])
app.include_router(process.router,   tags=["🤖 Phase 2 — Analyse IA"])
app.include_router(prospects.router, tags=["📋 Prospects"])

# ── Route de santé ────────────────────────────────────────────────────────────
@app.get("/", tags=["❤️ Health"])
def health():
    return {
        "status":  "ok",
        "service": "ISHOWO Prospection API",
        "phase":   "Phase 1 — Collecte de données",
        "docs":    "/docs",
    }
