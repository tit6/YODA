[2025-11-03] INIT        Repository Git initialisé
[2025-11-03] DESIGN      Définition de l’architecture Zero-Knowledge
[2025-11-05] DEVOPS      Docker & Docker Compose configurés
[2025-11-05] DEVOPS      Services : Frontend, Backend, MySQL, MinIO
[2025-11-07] DEVOPS      Volumes persistants MySQL / MinIO

[2025-11-10] FRONTEND    Initialisation Vue 3 + TypeScript + Vite
[2025-11-10] FRONTEND    Mise en place du router et vues de base
[2025-11-12] BACKEND     Initialisation Flask modulaire
[2025-11-12] BACKEND     Blueprints et configuration .env
[2025-11-14] DATABASE    Schéma MySQL initial (users, logs, folders)

[2025-12-01] AUTH        Endpoint /api/register implémenté
[2025-12-01] AUTH        Hash mots de passe (bcrypt)
[2025-12-03] AUTH        JWT login / middleware de protection
[2025-12-05] AUTH        Gestion sessions et infos utilisateur

[2025-12-08] FRONTEND    Vues Login / Auth / Validation email
[2025-12-08] FRONTEND    Store Pinia auth
[2025-12-10] FRONTEND    Connexion API & redirections

[2025-12-12] STORAGE     Intégration MinIO
[2025-12-12] STORAGE     Bucket yoda-documents créé
[2025-12-15] DATABASE    Table documents + métadonnées

[2026-01-05] CRYPTO      Génération clés RSA-4096 (client)
[2026-01-05] CRYPTO      Chiffrement AES-256-GCM par document
[2026-01-07] CRYPTO      Wrapping DEK avec clé publique
[2026-01-09] CRYPTO      Validation architecture Zero-Knowledge

[2026-01-12] SECURITY    Implémentation 2FA TOTP
[2026-01-14] SECURITY    Activation / vérification 2FA
[2026-01-16] FRONTEND    Interface 2FA (modals, vues)

[2026-01-19] SHARE       Table shared_files créée
[2026-01-21] SHARE       Chiffrement SEK pour partages
[2026-01-23] SHARE       Interface publique de partage

[2026-02-02] SECURITY    Renforcement validation mots de passe
[2026-02-02] SECURITY    Tracking tentatives de connexion échouées
[2026-02-04] TEST        Tests automatisés & linting
[2026-02-06] DOC         Documentation finale (README, OpenAPI)
[2026-02-06] RELEASE     Stabilisation & build final
