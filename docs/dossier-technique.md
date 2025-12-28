# Dossier technique — YODA (Coffre-fort numérique Zero-Knowledge)
**Version** : 0.2 (ébauche structurée “livrable”)  
**Date** : 2025-12-08  
**Licence** : MIT
---

## Table des matières
1. [Contexte et objectifs](#1-contexte-et-objectifs)  
2. [Périmètre fonctionnel](#2-périmètre-fonctionnel)  
   2.1. [Profils et responsabilités](#21-profils-et-responsabilités)  
   2.2. [Cas d’usage (scénarios)](#22-cas-dusage-scénarios)  
3. [Exigences non fonctionnelles](#3-exigences-non-fonctionnelles)  
4. [Architecture globale](#4-architecture-globale)  
   4.1. [Principes Zero-Knowledge](#41-principes-zero-knowledge)  
   4.2. [Composants techniques](#42-composants-techniques)  
   4.3. [Flux haut niveau](#43-flux-haut-niveau)  
5. [Structure du dépôt (convention projet)](#5-structure-du-dépôt-convention-projet)  
6. [Architecture cryptographique](#6-architecture-cryptographique)  
   6.1. [Primitives et paramètres](#61-primitives-et-paramètres)  
   6.2. [Gestion des clés (DEK / SEK / KEK)](#62-gestion-des-clés-dek--sek--kek)  
   6.3. [Dépôt document E2E (diagramme de séquence)](#63-dépôt-document-e2e-diagramme-de-séquence)  
   6.4. [Partage temporaire (diagramme de séquence)](#64-partage-temporaire-diagramme-de-séquence)  
   6.5. [Accès via lien (diagramme de séquence)](#65-accès-via-lien-diagramme-de-séquence)  
   6.6. [Export clé privée (format)](#66-export-clé-privée-format)  
7. [Modèle de données (conceptuel)](#7-modèle-de-données-conceptuel)  
   7.1. [Entités](#71-entités)  
   7.2. [Politique de rétention](#72-politique-de-rétention)  
8. [API REST — Spécification (OpenAPI 3.0)](#8-api-rest--spécification-openapi-30)  
   8.1. [Conventions](#81-conventions)  
   8.2. [Matrice des permissions (RBAC)](#82-matrice-des-permissions-rbac)  
   8.3. [Liste des endpoints](#83-liste-des-endpoints)  
   8.4. [Schémas (objets principaux)](#84-schémas-objets-principaux)  
9. [Stockage](#9-stockage)  
   9.1. [MySQL](#91-mysql)  
   9.2. [MinIO / S3](#92-minio--s3)  
10. [Intégrations externes](#10-intégrations-externes)  
11. [Sécurité applicative](#11-sécurité-applicative)  
12. [Déploiement (Docker Compose)](#12-déploiement-docker-compose)  
13. [Tests & Qualité](#13-tests--qualité)  
14. [Livrables de documentation](#14-livrables-de-documentation)  
15. [Risques, limites, décisions restantes](#15-risques-limites-décisions-restantes)  
16. [Annexes (glossaire)](#16-annexes-glossaire)  

---

## 1. Contexte et objectifs
YODA est une application web de coffre-fort numérique visant à stocker et partager des documents sensibles avec un niveau de confidentialité maximal.

Objectifs :
- Chiffrement end-to-end : documents chiffrés **avant** envoi au serveur
- Zero-Knowledge : le serveur ne détient jamais les clés de déchiffrement
- Partage temporaire sécurisé : liens expirants, accès lecture seule, mot de passe optionnel
- Authentification forte : mot de passe robuste + 2FA TOTP obligatoire

Publics cibles :
- Cabinets d’avocats, notaires, experts-comptables, recherche, administrations, secteurs régulés, PME, particuliers exigeants.

---

## 2. Périmètre fonctionnel

### 2.1. Profils et responsabilités
#### Administrateur
- CRUD utilisateurs
- Configuration politiques sécurité (MDP, 2FA, durée max des partages)
- Dashboard : statistiques (documents, utilisateurs actifs, partages)
- Ne peut pas accéder aux contenus (Zero-Knowledge)

#### Utilisateur standard
- Dépôt de documents (scan + chiffrement client)
- Organisation en dossiers (arborescence)
- Consultation documents (décryptage côté client)
- Partage temporaire (TTL, lecture seule, mot de passe)
- 2FA TOTP
- Accès à l’historique/logs d’accès à ses documents

### 2.2. Cas d’usage (scénarios)
- Inscription + activation email + activation 2FA + génération paire RSA
- Dépôt : scan VirusTotal côté client, DEK AES, chiffrement AES-GCM, wrapping DEK RSA, upload
- Partage : création lien, génération SEK, re-chiffrement côté serveur, SEK protégée par KDF (PBKDF2/Argon2id)
- Accès lien : saisie mot de passe, dérivation clé, déchiffrement local, rendu PDF en lecture seule UI
- Expiration : purge SEK/sel/métadonnées + logs archivés
- Export clé privée : chiffrement AES-GCM d’un export PKCS#8 protégé par passphrase

---

## 3. Exigences non fonctionnelles
- Sécurité :
  - AES-256-GCM, RSA-4096 (selon CDC), SHA-256
  - KDF : Argon2id (préféré) ou PBKDF2 (fallback)
  - 2FA TOTP obligatoire
- Traçabilité :
  - logs d’accès (horodatage, IP, user-agent, session)
  - audit append-only recommandé
- Performance :
  - upload/download fluides (documents ~5–50 Mo selon politique)
- Conformité :
  - minimisation des données, rétention configurable, export audit
- Disponibilité :
  - services séparés via Docker Compose (frontend, backend, mysql, minio)

---

## 4. Architecture globale

### 4.1. Principes Zero-Knowledge
- Le chiffrement/déchiffrement du document est réalisé **dans le navigateur**.
- Le backend ne reçoit jamais le fichier en clair.
- Le backend stocke :
  - blob chiffré (MinIO)
  - IV, empreintes
  - DEK chiffrée (wrapped DEK)
  - métadonnées document (nom, type, taille, dossier)
  - logs d’audit

### 4.2. Composants techniques
- Frontend : Vue 3 + TypeScript + Vite
- Backend : Flask API REST
- DB : MySQL 8
- Object storage : MinIO (S3 compatible)
- SMTP : activation email / notifications (si activé)
- APIs : VirusTotal (critique), HIBP (optionnel)

### 4.3. Flux haut niveau
- Upload : navigateur → VirusTotal → chiffrement WebCrypto → API → MinIO + MySQL
- Download : API → URL signée MinIO + métadonnées crypto → navigateur → déchiffrement local
- Partage : API crée token + re-chiffre blob pour partage + stocke crypto params + logs

---

## 5. Structure du dépôt (convention projet)
Structure attendue (d’après votre organisation) :
- `frontend/` : application Vue (src, build, config Vite)
- `backend/` : API Flask
- `database/` : scripts DB / initialisation
- `docs/` : documentation (dossier technique, OpenAPI, guides)
- `minio/` : éléments de configuration / seed (si utilisés)
- `docker-compose.yml` : orchestration services
- `.env` : variables d’environnement (dev)
- `.github/` : CI/CD (workflows)
- `LICENSE` : MIT

Recommandations de normalisation doc :
- un seul fichier racine : `README.md` (éviter doublon `readme.md`)
- placer OpenAPI dans `docs/openapi.yaml`
- placer ce dossier technique dans `docs/dossier-technique.md`

---

## 6. Architecture cryptographique

### 6.1. Primitives et paramètres
- Chiffrement contenu : AES-256-GCM
  - IV recommandé : 12 octets aléatoires
  - Tag d’auth : géré par GCM
- Empreinte : SHA-256 (hex ou base64, standardiser)
- Enveloppe DEK : RSA-4096 (OAEP recommandé si vous choisissez le padding)
- KDF :
  - Argon2id (paramètres à fixer : mémoire/itérations/parallélisme)
  - PBKDF2 fallback (ex : HMAC-SHA-256 + itérations élevées)

> Standardisation recommandée : définir dans la doc le format encodage (Base64 standard, pas Base64URL sauf tokens).

### 6.2. Gestion des clés (DEK / SEK / KEK)
- DEK (Data Encryption Key) : générée côté client, 256 bits, par document (ou par version)
- Wrapped DEK : DEK chiffrée avec la clé publique RSA de l’utilisateur
- SEK (Share Encryption Key) : générée côté serveur pour un partage, 256 bits
- KEK (Key Encryption Key) :
  - dérivée d’un mot de passe de partage (protège SEK)
  - dérivée d’une passphrase d’export (protège clé privée exportée)

### 6.3. Dépôt document E2E (diagramme de séquence)


---

## 7. Modèle de données (conceptuel)

### 7.1. Entités
- `users`
  - `id` (UUID), `email`, `role`, `password_hash`, `status`, `created_at`
- `user_security`
  - `user_id`, `totp_enabled`, `totp_secret_encrypted` (si stocké), `recovery_codes_hash`
- `user_keys`
  - `user_id`, `public_key_pem`, `public_key_sha256`, `created_at`, `revoked_at`
- `folders`
  - `id`, `user_id`, `parent_id`, `name`, `created_at`
- `documents`
  - `id`, `user_id`, `folder_id`, `filename`, `mime_type`, `size_bytes`, `sha256_original`, `created_at`
- `document_versions`
  - `id`, `document_id`, `object_key`, `iv_base64`, `wrapped_dek_base64`, `created_at`, `status`
- `shares`
  - `id`, `token`, `document_version_id`, `expires_at`, `policy_json`
  - `encrypted_sek_base64`, `salt_base64`, `iv_base64`, `kdf_params_json`
  - `share_object_key`
- `audit_logs`
  - `id`, `actor_user_id` (nullable pour accès public), `action`, `target_type`, `target_id`
  - `ip`, `user_agent`, `session_id`, `created_at`, `metadata_json`
- `virustotal_scans`
  - `id`, `user_id`, `sha256`, `verdict`, `score`, `raw_json`, `created_at`

> Note : le stockage exact du secret TOTP est une décision de sécurité. Alternative : ne pas le stocker en clair, ou stocker uniquement des paramètres + secret chiffré serveur (mais attention à la logique Zero-Knowledge : le TOTP n’est pas lié au contenu document, donc ce point est acceptable côté serveur si bien protégé).

### 7.2. Politique de rétention
- Partages : suppression à expiration (métadonnées + objet MinIO)
- Logs d’audit : rétention configurable (ex : 12–24 mois)
- Scans VirusTotal : rétention configurable, minimiser les données conservées

---

## 8. API REST — Spécification (OpenAPI 3.0)

### 8.1. Conventions
- Base : `/api`
- Auth : JWT Bearer
- UUID pour ressources
- Réponses standard :
  - `{"status":"success","data":...,"message":...}`
  - `{"status":"error","code":"...","message":"..."}`

### 8.2. Matrice des permissions (RBAC)
| Action | Utilisateur standard | Administrateur |
|---|---:|---:|
| S’inscrire / activer compte | Oui | Oui |
| Se connecter + 2FA | Oui | Oui |
| Gérer ses clés publiques | Oui | Oui |
| CRUD dossiers personnels | Oui | Oui (pour soi) |
| Upload / download ses documents | Oui | Oui (pour soi) |
| Lire logs de ses documents | Oui | Oui (pour soi) |
| Créer un partage | Oui | Oui |
| Consulter dashboard global | Non | Oui |
| CRUD utilisateurs | Non | Oui |
| Modifier politiques sécurité globales | Non | Oui |
| Accéder contenu documents d’autrui | Non | Non |

### 8.3. Liste des endpoints
#### Auth
- `POST /auth/register`
- `POST /auth/activate` (token email)
- `POST /auth/login`
- `POST /auth/2fa/setup`
- `POST /auth/2fa/verify`
- `POST /auth/2fa/disable` (optionnel, selon politique)
- `POST /auth/recovery-codes/regenerate`
- `POST /auth/logout` (optionnel si JWT stateless)

#### Utilisateur
- `GET /users/me`
- `PUT /users/me/public-key`
- `GET /users/me/security` (statut 2FA, etc.)

#### Dossiers
- `GET /folders`
- `POST /folders`
- `PATCH /folders/{id}`
- `DELETE /folders/{id}`

#### Documents
- `GET /documents?folderId=...`
- `POST /documents` (création métadonnées + crypto params)
- `PUT /documents/{id}/content` (upload ciphertext)
- `GET /documents/{id}`
- `GET /documents/{id}/download` (retourne URL signée + iv + wrappedDEK)
- `POST /documents/{id}/versions` (optionnel si versioning séparé)
- `GET /documents/{id}/access-logs`

#### Partages
- `POST /shares`
- `GET /shares/{token}` (public, métadonnées crypto/policy)
- `GET /shares/{token}/download` (URL signée de l’objet chiffré partagé)
- `DELETE /shares/{token}` (révocation par owner)

#### Audit
- `GET /audit/me` (logs utilisateur)
- `GET /admin/audit` (admin)

#### Admin
- `GET /admin/dashboard/stats`
- `GET /admin/users`
- `POST /admin/users`
- `PATCH /admin/users/{id}`
- `DELETE /admin/users/{id}`
- `GET /admin/security-policies`
- `PATCH /admin/security-policies`

### 8.4. Schémas (objets principaux)
Champs recommandés (extraits) :
- `DocumentCrypto`
  - `ivBase64`, `wrappedDekBase64`, `sha256Original`
- `ShareCrypto`
  - `encryptedSekBase64`, `saltBase64`, `ivBase64`, `kdfParams`
- `AuditEvent`
  - `action`, `targetType`, `targetId`, `createdAt`, `ip`, `userAgent`

---

## 9. Stockage

### 9.1. MySQL
- Source de vérité : métadonnées, ACL, logs, paramètres crypto non secrets (IV, salts)
- Index recommandés :
  - `documents(user_id, folder_id)`
  - `shares(token)` unique
  - `audit_logs(actor_user_id, created_at)`
- Contraintes :
  - tokens partage uniques et non devinables (longs, aléatoires)

### 9.2. MinIO / S3
- Buckets :
  - `vault-documents`
  - `vault-shares`
- Clés d’objets (convention) :
  - `documents/{userId}/{documentId}/{versionId}.bin`
  - `shares/{token}.bin`
- URLs signées :
  - durée courte (ex : 60–300 s)
  - génération côté backend après contrôle d’accès

---

## 10. Intégrations externes

### VirusTotal (critique)
- Le client soumet le fichier avant chiffrement
- Règle : si détection > seuil (ex : >3 moteurs) → rejet
- Conservation : verdict + hash + trace pour audit

### Have I Been Pwned (optionnel)
- Vérifier l’email à l’inscription
- Mode recommandé : avertissement + renforcement (forcer 2FA, exiger MDP unique)

---

## 11. Sécurité applicative
- Mots de passe :
  - politique min 16 + complexité
  - protection brute-force (rate limiting + backoff)
- 2FA :
  - TOTP obligatoire
  - codes de récupération (hashés en DB)
- Sessions / JWT :
  - expiration courte
  - distinction “2FA validée” vs “en attente 2FA”
- Frontend :
  - CSP stricte
  - validation des inputs
  - prévention XSS (priorité)
- API :
  - validation schémas
  - contrôle d’accès systématique (owner, rôle)
- Partages publics :
  - endpoints minimalistes
  - journalisation systématique

---

## 12. Déploiement (Docker Compose)
Services minimum :
- `frontend` : Vue (dev server ou build)
- `backend` : Flask API
- `database` : MySQL 8
- `minio` : S3 compatible

Variables d’environnement (noms, valeurs à fournir via `.env`) :
- `JWT_SECRET=<placeholder>`
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`
- `VIRUSTOTAL_API_KEY=<placeholder>`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD=<placeholder>`

Recommandations prod :
- HTTPS obligatoire
- rotation secrets
- ports internes non exposés
- sauvegardes MySQL + lifecycle MinIO
- CI/CD : build + tests + scan dépendances

---

## 13. Tests & Qualité
Objectif : couverture backend ≥ 50% (pytest + pytest-cov)

Priorités tests :
- Auth : login, 2FA, tokens JWT
- Documents : contrôle d’accès, création, download (URL signée)
- Partages : TTL, révocation, accès public, purge
- Audit : présence et cohérence des événements
- VirusTotal : mocks (pas d’appel réseau en tests)

Qualité :
- lint/format (à définir : ruff/black/isort côté Python, eslint/prettier côté TS)
- docstrings PEP257 sur fonctions crypto / auth

---

## 14. Livrables de documentation
- `README.md` : installation, lancement, variables env, troubleshooting
- `docs/dossier-technique.md` : ce document
- `docs/openapi.yaml` : API complète
- `SECURITY.md` : architecture Zero-Knowledge, crypto, disclosure vulnérabilités
- Guide utilisateur PDF/HTML : parcours (user/admin) + bonnes pratiques

---

## 15. Risques, limites, décisions restantes
- “Lecture seule” sur navigateur : limitation intrinsèque (UI seulement)
- XSS / supply-chain : risque critique (CSP + dépendances + revue)
- Perte clé privée : exiger/exporter un backup chiffré (et sensibiliser)
- Paramètres KDF : fixer et documenter (sécurité vs performance)
- Inaltérabilité audit : décider append-only simple vs chaînage (hash chain)

---

## 16. Annexes (glossaire)
- Zero-Knowledge : serveur incapable de déchiffrer les contenus
- DEK : Data Encryption Key (clé AES par document)
- SEK : Share Encryption Key (clé AES par partage)
- KEK : Key Encryption Key (clé dérivée d’un mot de passe)
- IV : vecteur d’initialisation (AES-GCM)
- KDF : fonction de dérivation de clé (Argon2id/PBKDF2)
- TOTP : code à usage temporaire (2FA)

---