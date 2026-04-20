"""
Seed de test — Phase 1
Insère des prospects béninois fictifs pour tester le pipeline
sans avoir besoin de scraper le web.

Usage : python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database.session import SessionLocal, engine, Base
from app.repository.prospect_repository import ProspectRepository
from app.schemas.prospect import ProspectCreate

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

PROSPECTS_TEST = [
    {
        "nom": "Pharmacie La Croix Bleue",
        "secteur": "Santé / Pharmacie",
        "ville": "Cotonou",
        "telephone": "97123456",
        "description": "Grande pharmacie bien approvisionnée, médicaments et produits parapharmaceutiques en gros et détail.",
        "source": "seed",
    },
    {
        "nom": "Épicerie du Grand Marché Dantokpa",
        "secteur": "Commerce alimentaire",
        "ville": "Cotonou",
        "telephone": "96234567",
        "description": "Épicerie avec large gamme de produits alimentaires, boissons, condiments. Stock important.",
        "source": "seed",
    },
    {
        "nom": "Quincaillerie Centrale Bénin",
        "secteur": "Quincaillerie / BTP",
        "ville": "Porto-Novo",
        "telephone": "95345678",
        "description": "Matériaux de construction, outillage, plomberie et électricité. Vente en gros et détail.",
        "source": "seed",
    },
    {
        "nom": "Restaurant Chez Maman Africa",
        "secteur": "Restauration",
        "ville": "Cotonou",
        "telephone": "94456789",
        "description": "Cuisine béninoise traditionnelle, repas chauds, livraison disponible.",
        "source": "seed",
    },
    {
        "nom": "Supermarché City Market Parakou",
        "secteur": "Grande distribution",
        "ville": "Parakou",
        "telephone": "97567890",
        "description": "Supermarché avec rayon alimentaire, électroménager, hygiène. Grand volume de stock.",
        "source": "seed",
    },
    {
        "nom": "Cabinet Conseil RH Excellence",
        "secteur": "Services / Ressources Humaines",
        "ville": "Cotonou",
        "telephone": "96678901",
        "description": "Recrutement, formation et gestion des ressources humaines pour PME.",
        "source": "seed",
    },
    {
        "nom": "Droguerie Produits Ménagers Plus",
        "secteur": "Droguerie",
        "ville": "Abomey-Calavi",
        "telephone": "95789012",
        "description": "Produits d'entretien, détergents, désinfectants. Livraison sur Cotonou.",
        "source": "seed",
    },
    {
        "nom": "Boutique Mode Africaine Tendance",
        "secteur": "Textile / Mode",
        "ville": "Cotonou",
        "telephone": "+22994890123",
        "description": "Pagnes wax, tenues africaines, prêt-à-porter. Grand choix de tissus.",
        "source": "seed",
    },
]


def main():
    db   = SessionLocal()
    repo = ProspectRepository(db)
    ok, skip = 0, 0

    print("\n🌱 Démarrage du seed ISHOWO...\n")

    for data in PROSPECTS_TEST:
        try:
            schema  = ProspectCreate(**data)
            resultat = repo.creer(schema)
            if resultat:
                print(f"  ✅  {resultat.nom:<40} {resultat.telephone}")
                ok += 1
            else:
                print(f"  ⚠️  Doublon ignoré : {data['nom']}")
                skip += 1
        except Exception as e:
            print(f"  ❌  Erreur [{data['nom']}] : {e}")

    db.close()
    print(f"\n✨ Terminé : {ok} insérés, {skip} doublons ignorés.")
    print("👉 Lancez l'API : uvicorn app.main:app --reload")
    print("👉 Swagger UI  : http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
