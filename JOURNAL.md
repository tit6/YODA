# Journal de Développement - YODA (Coffre-fort Numérique)

**Projet** : Application de coffre-fort numérique sécurisé avec chiffrement end-to-end  
**Licence** : MIT  
**Dernière mise à jour** : 06/02/2026

---

## Initialisation du projet et infrastructure de base

**Infrastructure & DevOps**
- Mise en place de l'architecture Docker avec Docker Compose
- Configuration de 4 services conteneurisés :
  - Frontend (Vue.js/Vite) - port 5173
  - Backend (Flask Python) - port 5000
  - Database (MySQL 8.0) - port 3306
  - MinIO (stockage S3-compatible) - ports 9000/9001
- Création des volumes persistants pour MySQL et MinIO
- Configuration initiale du repository Git
- Mise en place des workflows CI/CD avec GitHub Actions

**Frontend - Base Vue.js**
- Initialisation du projet Vue 3 avec TypeScript et Vite
- Configuration du router Vue Router
- Structure de base des vues (authentication, dashboard)
- Configuration TypeScript (tsconfig.json, tsconfig.app.json, tsconfig.node.json)
- Setup de l'environnement de développement

**Backend - Base Flask**
- Création de l'application Flask avec structure modulaire
- Configuration des blueprints pour organiser les routes
- Mise en place de la structure de dossiers :
  - `module/` : modules partagés (config, db, crypto, JWT, middleware)
  - `routes/` : endpoints API (auth, user, documents, share, health)
  - `static/` : fichiers statiques (OpenAPI spec)
- Configuration de l'environnement avec fichier `.env`
- Intégration de python-dotenv pour la gestion des variables d'environnement

**Base de données - Schéma initial**
- Création du schéma MySQL avec 3 tables de base :
  - `users` : gestion des utilisateurs (id, nom, prenom, email, mdp)
  - `logs` : audit trail des actions utilisateur
  - `folders` : organisation hiérarchique des documents

---

## Développement Backend/Frontend et authentification

**Système d'authentification**
- Implémentation de l'inscription utilisateur (`/api/register`)
- Hash des mots de passe avec bcrypt ($2b$12$)
- Système de connexion avec JWT (`/api/login`)
- Middleware d'authentification pour protéger les routes
- Gestion des sessions avec tokens JWT
- Endpoint de vérification du statut de session (`/api/statue_session`)

**Gestion des utilisateurs**
- Endpoint pour récupérer les informations utilisateur (`/api/name_user`)
- Fonction de changement de mot de passe (`/api/change_password`)
- Validation des données utilisateur
- Gestion des erreurs et retours API standardisés

**Frontend - Interface d'authentification**
- Création des vues d'authentification :
  - `LoginView.vue` : page de connexion
  - `AuthProcessView.vue` : processus d'authentification
  - `EmailValidationView.vue` : validation d'email
- Store Pinia pour la gestion de l'état d'authentification (`auth.ts`)
- Intégration des appels API avec fetch
- Gestion des redirections après connexion

**Modules Backend**
- `module/db.py` : connexion et requêtes MySQL avec curseur dictionnaire
- `module/jwt_ag.py` : génération et validation des tokens JWT
- `module/config.py` : centralisation de la configuration (DB, secret keys)
- `module/middleware.py` : middleware d'authentification avec chemins publics
- `module/api_retour.py` : standardisation des réponses API

---

## Intégration MinIO, Documents et Cryptographie

**Intégration MinIO**
- Configuration du client MinIO dans `module/minio_client.py`
- Création automatique du bucket `yoda-documents` au démarrage
- Configuration des credentials (minioadmin/minioadmin)
- Gestion des URLs pre-signées pour l'upload/download sécurisé
- Connexion entre backend et MinIO via réseau Docker

**Système de gestion de documents**
- Extension du schéma de base de données :
  - Table `documents` avec champs de chiffrement (dek_encrypted, iv, sha256)
  - Support des métadonnées (nom_original, extension, taille_octets)
  - Liaison avec folders et users
- Routes de gestion de documents :
  - Upload de documents chiffrés
  - Liste des documents par utilisateur
  - Téléchargement sécurisé
  - Organisation en dossiers

**Architecture cryptographique Zero-Knowledge**
- Implémentation du chiffrement côté client avec WebCrypto API
- Génération de paires de clés RSA-4096 par utilisateur
- Système de clés DEK (Data Encryption Key) :
  - Génération AES-256-GCM pour chaque document
  - Wrapping de la DEK avec la clé publique RSA de l'utilisateur
- Module `module/crypto.py` pour les opérations cryptographiques serveur
- Store frontend `crypto.ts` pour les opérations client :
  - Génération de clés RSA
  - Chiffrement/déchiffrement AES-GCM
  - Gestion des IV (Initialization Vectors)
  - Calcul de hash SHA-256

**Stockage des clés publiques**
- Table étendue `users` avec champ `public_key`
- Endpoints pour sauvegarder/récupérer la clé publique RSA (`/api/user/public-key`)
- Format PEM pour le stockage des clés
- Validation de l'intégrité des clés

**Frontend - Interface de documents**
- Vue `DocumentsView.vue` pour la gestion des documents
- Store Pinia `documents.ts` pour l'état des documents
- Modal d'upload avec support du drag & drop
- Interface de liste des documents avec métadonnées
- Gestion du chiffrement/déchiffrement dans le navigateur

---

## Authentification à deux facteurs (2FA) et amélioration de la sécurité

**Implémentation du 2FA TOTP**
- Intégration de PyOTP pour la génération de secrets TOTP
- Route d'activation 2FA (`/api/a2f`) :
  - Génération de secret TOTP
  - Chiffrement du secret avec APP_MASTER_KEY (AES-256)
  - Génération de QR code pour Google Authenticator
  - Vérification du premier code avant activation
- Route de vérification 2FA lors de la connexion (`/api/verify-2fa`)
- Endpoint pour vérifier le statut 2FA (`/api/statue_a2f`)
- Route de désactivation 2FA avec vérification du code

**Gestion sécurisée des secrets 2FA**
- Génération automatique de `APP_MASTER_KEY` si absente
- Stockage du secret 2FA chiffré dans la table `users` (champ `secret_a2f`)
- Statut 2FA dans `statue_a2f` (0=désactivé, 1=activé)
- Module de chiffrement AES-256 pour protéger les secrets TOTP

**Frontend - Interface 2FA**
- Vue `Verify2FAView.vue` pour la saisie du code TOTP
- Composant modal `ActivateA2FModal.vue` pour l'activation
- Composant modal `DisableA2FModal.vue` pour la désactivation
- Affichage du QR code pour la configuration
- Gestion des états d'activation dans le store auth

**Amélioration du middleware**
- Gestion des tokens temporaires A2F
- Routes publiques étendues pour le processus 2FA
- Validation des tokens JWT avec gestion des payloads A2F

---

## Partage sécurisé et export/import de clés

**Système de partage sécurisé de documents**
- Création de la table `shared_files` :
  - Gestion des liens de partage avec tokens uniques
  - Support de l'expiration temporelle (`expires_at`)
  - Compteur de vues (`views_count`, `max_views`)
  - Activation/désactivation des partages (`is_active`)
  - Chiffrement avec SEK (Share Encryption Key)
- Routes de partage (`routes/share/share.py`) :
  - `/api/share/upload` : création d'un partage chiffré
  - `/api/share/list` : liste des documents partagés par l'utilisateur
  - `/api/share/switch` : activation/désactivation d'un partage
  - `/api/share/name_file` : récupération des métadonnées
  - `/api/share/download` : téléchargement via lien de partage

**Cryptographie du partage**
- Génération de SEK (Share Encryption Key) côté serveur
- Re-chiffrement du document avec la SEK pour le partage
- Protection de la SEK avec mot de passe optionnel (KDF)
- IV distinct pour chaque partage
- Hash SHA-256 pour vérification d'intégrité

**Frontend - Interface de partage**
- Vue `SharedDocumentsView.vue` pour gérer les partages
- Vue `PublicSharedView.vue` pour accéder aux liens publics
- Vue `share.vue` pour les accès visiteurs
- Store `share_fonction.ts` pour la logique de partage
- Store `share_crypto.ts` pour le chiffrement de partage
- Composants modaux :
  - `showCreateModal.vue` : création de lien de partage
  - `showLinkModal.vue` : affichage et copie du lien
- Gestion de l'expiration et des limites de vues

**Export/Import de clés privées**
- Fonctionnalité d'export de clé privée chiffrée :
  - Chiffrement de la clé privée avec passphrase utilisateur
  - Format PKCS#8 pour la clé
  - Protection AES-256-GCM avec KDF
  - Téléchargement du fichier `.key` chiffré
- Fonctionnalité d'import de clé privée :
  - Déchiffrement avec passphrase
  - Validation de l'intégrité
  - Restauration dans le navigateur
- Composants frontend :
  - `ExportPrivateKeyModal.vue` : modal d'export
  - `ImportPrivateKeyModal.vue` : modal d'import
- Module cryptographique `PrivateKeyExport` dans `crypto.ts`

**Amélioration de la base de données**
- Optimisation des index pour les requêtes de partage
- Constraints de clés étrangères avec CASCADE

---

## Documentation, Tests et CI/CD

**Documentation technique complète**
- Création du dossier technique (`docs/dossier-technique.md`) :
  - Architecture Zero-Knowledge détaillée
  - Diagrammes de séquence pour les flux critiques
  - Spécifications cryptographiques (AES-256-GCM, RSA-4096)
  - Modèle de données conceptuel
  - Matrice de permissions RBAC
- Mise à jour du README.md avec :
  - Instructions d'installation complètes
  - Documentation des services et ports
  - Commandes Docker utiles
  - Prérequis et configuration
- Spécification OpenAPI 3.0 (`static/openapi.yaml`) :
  - Documentation de tous les endpoints
  - Schémas de requêtes/réponses
  - Authentification JWT documentée
  - Exemples d'utilisation

**Tests et Qualité**
- Configuration des tests backend :
  - Tests d'authentification (register, login, 2FA)
  - Tests de validation de mot de passe
  - Tests de gestion de documents (upload, list, download)
  - Tests des endpoints protégés
  - Validation JSON des requêtes
- Intégration de pytest pour les tests Python
- Configuration du linting :
  - Python : vérification de la qualité du code
  - TypeScript : ESLint pour le frontend
- Tests de sécurité :
  - Validation des mots de passe forts
  - Vérification des tokens JWT
  - Tests d'authentification

**CI/CD avec GitHub Actions**
- Workflow d'intégration continue :
  - Build automatique des conteneurs Docker
  - Exécution des tests backend
  - Vérification de l'état des services (health checks)
  - Tests des endpoints API
  - Linting du code Python et TypeScript
- Configuration multi-branches (main, development, ci_cd)
- Création de fichier `.env.example` pour la documentation
- Health check endpoint (`/api/health`) pour le monitoring

**Refactoring et optimisation**
- Réorganisation du code backend :
  - Séparation claire des blueprints
  - Modularisation des fonctions cryptographiques
  - Amélioration de la gestion des erreurs
- Refactoring frontend :
  - Composants réutilisables pour les modaux
  - Stores Pinia optimisés
  - Amélioration de la gestion d'état
- Suppression du code redondant et inutilisé

---

## Sécurité avancée et audit

**Renforcement de la sécurité**
- Validation renforcée des mots de passe :
  - Longueur minimale
  - Complexité (majuscules, minuscules, chiffres, caractères spéciaux)
  - Vérification de la conformité des mots de passe
- Gestion des tentatives de connexion échouées :
  - Table `failed_login_attempts` pour tracker les échecs
  - Logging de l'IP et du timestamp
  - Base pour implémentation future de rate limiting
- Amélioration du chiffrement :
  - Vérification systématique de APP_MASTER_KEY
  - Validation de l'encodage des mots de passe
  - Gestion sécurisée des IV et salts

**Système d'audit et logs**
- Table `shared_acces_log` pour auditer les accès aux partages :
  - Tracking des accès avec IP et User-Agent
  - Horodatage précis des consultations
  - Référence au fichier partagé
  - Base pour détection d'anomalies
- Amélioration de la table `logs` :
  - Ajout du champ IP pour tous les logs
  - Statut des actions (succès/échec)
  - Timestamp automatique
- Logging des échecs de connexion avec IP

**Protection anti-attaques**
- Logs d'accès aux documents partagés pour détecter les abus
- Structure pour prévenir les attaques par force brute
- Monitoring des tentatives de connexion suspectes
- Préparation pour rate limiting et blocage d'IP

**Frontend - Améliorations UX/UI**
- Création de la page d'accueil (`HomeView.vue`)
- Amélioration du layout dashboard (`DashboardLayout.vue`)
- Refactoring des composants d'account :
  - Modularisation des modaux 2FA
  - Amélioration de l'interface de gestion de clés
- Assets visuels :
  - Création d'icônes SVG personnalisées (Document, Security, Share, etc.)
  - Variables CSS pour cohérence visuelle
  - Styles des composants harmonisés

**Organisation du code**
- Refactoring de l'arborescence frontend :
  - Séparation claire views/components
  - Organisation par feature (authentication, dashboard, share)
  - Composants réutilisables dans assets/icons
- Structure backend optimisée :
  - Routes organisées par domaine fonctionnel
  - Modules partagés bien définis
  - Séparation des responsabilités

---

## Perfectionnement et stabilisation

**Corrections et améliorations**
- Fix des problèmes d'insertion en base de données
- Correction de la gestion de l'état des fichiers (endpoint 404/401)
- Amélioration de la gestion des erreurs API
- Optimisation des requêtes de base de données
- Validation améliorée des requêtes JSON

**Documentation continue**
- Mise à jour de la spécification OpenAPI pour :
  - Support de la gestion chiffrée des documents
  - Gestion des clés publiques RSA
  - Endpoints de partage documentés
- Amélioration du README avec exemples d'utilisation
- Documentation des variables d'environnement
- Guide de déploiement Docker

**Nettoyage et optimisation**
- Suppression de `testdb.vue` inutilisé
- Nettoyage des imports redondants
- Optimisation de la configuration Ruff
- Mise à jour de LICENSE
- Refactoring pour améliorer la maintenabilité

**État actuel du projet**
- Infrastructure Docker complète et fonctionnelle
- Backend Flask avec API REST sécurisée
- Frontend Vue 3 avec TypeScript
- Authentification JWT + 2FA TOTP obligatoire
- Chiffrement end-to-end avec Zero-Knowledge
- Système de partage temporaire sécurisé
- Gestion de clés RSA avec export/import
- Stockage MinIO avec chiffrement
- Base de données MySQL avec audit logs
- CI/CD avec GitHub Actions
- Documentation technique complète
- Tests automatisés

---

## Fonctionnalités principales implémentées

### Authentification & Sécurité
- Inscription utilisateur avec validation email
- Connexion avec JWT
- 2FA TOTP obligatoire (Google Authenticator)
- Gestion de session sécurisée
- Changement de mot de passe
- Validation de la complexité des mots de passe
- Middleware de protection des routes
- Logs d'authentification et tentatives échouées

### Cryptographie Zero-Knowledge
- Génération de paires de clés RSA-4096 côté client
- Chiffrement AES-256-GCM des documents
- Système de DEK (Data Encryption Key) par document
- Wrapping DEK avec clé publique RSA
- Hash SHA-256 pour intégrité
- Le serveur ne voit jamais les données en clair
- Export/Import de clés privées chiffrées

### Gestion de Documents
- Upload de documents chiffrés (côté client)
- Organisation en dossiers hiérarchiques
- Liste et recherche de documents
- Téléchargement avec déchiffrement client
- Métadonnées (nom, type, taille, date)
- Stockage sécurisé dans MinIO
- Gestion des versions

### Partage Sécurisé
- Création de liens de partage temporaires
- Expiration configurable
- Limite de vues optionnelle
- Protection par mot de passe optionnelle
- SEK (Share Encryption Key) unique par partage
- Activation/désactivation des partages
- Logs d'accès aux partages (IP, User-Agent)
- Interface publique pour accès visiteur

### Audit & Monitoring
- Logs de toutes les actions utilisateur
- Tracking des accès aux documents partagés
- Logs des tentatives de connexion échouées
- Horodatage et IP de toutes les actions
- Health check pour monitoring
- Statistiques d'utilisation

### Infrastructure & DevOps
- Architecture Docker multi-services
- Docker Compose pour orchestration
- CI/CD GitHub Actions
- Tests automatisés (backend)
- Linting Python et TypeScript
- Variables d'environnement sécurisées
- Volumes persistants pour données

---

## Stack Technique

### Frontend
- **Framework** : Vue.js 3 (Composition API)
- **Langage** : TypeScript
- **Build** : Vite
- **Router** : Vue Router 4
- **State** : Pinia
- **Crypto** : Web Crypto API
- **Styling** : CSS3 custom properties

### Backend
- **Framework** : Flask (Python 3.x)
- **Auth** : JWT + PyOTP (TOTP)
- **Crypto** : cryptography (AES-256, RSA-4096)
- **Password** : bcrypt
- **Database** : PyMySQL
- **Storage** : MinIO Python SDK
- **CORS** : Flask-CORS

### Infrastructure
- **Base de données** : MySQL 8.0
- **Stockage objet** : MinIO (S3-compatible)
- **Conteneurisation** : Docker + Docker Compose
- **CI/CD** : GitHub Actions
- **Versionning** : Git

### Sécurité
- **Chiffrement documents** : AES-256-GCM
- **Clés asymétriques** : RSA-4096
- **Hash** : SHA-256
- **KDF** : PBKDF2 / Argon2id (recommandé)
- **2FA** : TOTP (RFC 6238)
- **Token** : JWT (HS256)

---

## Déploiement

Le projet est déployable avec une seule commande :
```bash
docker compose up -d
```

**Services disponibles** :
- Frontend : http://localhost:5173
- Backend API : http://localhost:5000
- MinIO Console : http://localhost:9001
- MySQL : localhost:3306

**Compte de test** :
- Email : 
- Password : 

---

## Prochaines étapes (backlog)

- [ ] Intégration VirusTotal pour scan des fichiers
- [ ] API HIBP pour vérification des mots de passe compromis
- [ ] Export d'audit logs
- [ ] Recovery codes pour 2FA

---

**Titouan PELOU - Louis PERROUX - Gwenvaël CAOUISSIN | Licence MIT**



