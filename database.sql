-- ============================================================
-- ISHOWO Prospection — Script de création BDD MySQL 8.0+
-- Usage : mysql -u root -p < database.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS ishowo_prospects
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ishowo_prospects;

-- Table principale des prospects
CREATE TABLE IF NOT EXISTS prospects (
    id          INT AUTO_INCREMENT PRIMARY KEY,

    -- Données collectées (Phase 1)
    nom         VARCHAR(255) NOT NULL,
    secteur     VARCHAR(255),
    ville       VARCHAR(100),
    telephone   VARCHAR(30) UNIQUE,          -- dédoublonnage clé
    description TEXT,
    source      VARCHAR(100),                -- "goafrica" | "google"

    -- Champs IA (remplis en Phase 2)
    categorie           VARCHAR(100),
    score_ia            VARCHAR(10),
    pertinence_ishowo   VARCHAR(10),
    justification_ia    TEXT,

    -- Statut du pipeline
    statut ENUM('raw', 'processed', 'scored') NOT NULL DEFAULT 'raw',

    -- Horodatage
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,

    -- Index pour les requêtes fréquentes
    INDEX idx_statut  (statut),
    INDEX idx_source  (source),
    INDEX idx_ville   (ville)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vérification
SELECT 'Table prospects créée avec succès ✅' AS message;
