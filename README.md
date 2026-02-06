# YODA - Coffre-fort Numérique

Application de coffre-fort numérique sécurisé avec chiffrement end-to-end Zero-Knowledge.

## Fonctionnalités principales

- **Upload & téléchargement de documents** - Chiffrement côté client avec AES-256-GCM
- **Authentification sécurisée** - JWT + 2FA TOTP obligatoire
- **Gestion cryptographique** - RSA-4096 pour les clés, AES-256 pour le chiffrement
- **Organisation des fichiers** - Stockage dans MinIO avec métadonnées chiffrées
- **Partage sécurisé** - Liens temporaires avec expiration et protection optionnelle
- **Audit complet** - Logs de toutes les actions utilisateur avec IP et horodatage
- **Export/Import de clés** - Sauvegarde et restauration sécurisée des clés privées
- **API REST complète** - Documentation avec OpenAPI/Swagger

## Architecture

- **Frontend** : Vue.js 3 + TypeScript + Vite
- **Backend** : Python Flask + API REST
- **Database** : MySQL 8.0
- **Storage** : MinIO (stockage d'objets compatible S3)
- **Containerisation** : Docker + Docker Compose

## Prérequis

- Docker Desktop (ou Docker Engine + Docker Compose)
- Git

## Installation

1. **Cloner le projet**
```bash
git clone https://github.com/tit6/YODA.git
cd YODA
```

2. **Créer le fichier `.env`** (déjà présent, modifier si nécessaire)
```env
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=yoda
DATABASE_HOST=database
DATABASE_PORT=3306
DATABASE_NAME=yoda
DATABASE_USER=root
DATABASE_PASSWORD=root
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

3. **Lancer l'application**
```bash
docker compose up -d
```

## Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Interface utilisateur Vue.js |
| Backend | http://localhost:5000 | API REST Flask |
| MinIO Console | http://localhost:9001 | Interface d'administration MinIO |
| MinIO API | http://localhost:9000 | API S3 compatible |
| MySQL | localhost:3306 | Base de données |

### Identifiants MinIO
- **Username** : `minioadmin`
- **Password** : `minioadmin`

**Compte de test** :
- Email : `test@gmail.com`
- Mot de passe : voir hash bcrypt dans `database/schemas.sql`

## Commandes utiles

### Docker

```bash
# Démarrer tous les conteneurs
docker compose up -d

# Voir les logs
docker compose logs -f

# Logs d'un service spécifique
docker logs yoda-frontend
docker logs yoda-backend
docker logs yoda-database
docker logs yoda-minio

# Arrêter les conteneurs
docker compose down

# Arrêter et supprimer les volumes
docker compose down -v

# Rebuild un service spécifique
docker compose build backend
docker compose build frontend

# Rebuild complet
docker compose up --build

# Redémarrer un service
docker compose restart backend
docker compose restart frontend
```

### Tests

```bash
# Tester le backend
curl http://localhost:5000/coucou
curl http://localhost:5000/db-test

# Entrer dans un conteneur
docker exec -it yoda-backend bash
docker exec -it yoda-frontend sh
docker exec -it yoda-database bash
```

### Base de données

```bash
# Se connecter à MySQL
docker exec -it yoda-database mysql -u root -proot yoda

# Backup de la base
docker exec yoda-database mysqldump -u root -proot yoda > backup.sql

# Restaurer la base
docker exec -i yoda-database mysql -u root -proot yoda < backup.sql
```

## Structure du projet

```
YODA/
├── backend/              # API Flask Python
│   ├── app.py           # Point d'entrée
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── module/          # Modules partagés (crypto, db, jwt, middleware)
│   ├── routes/          # Endpoints API (auth, documents, share, user)
│   └── static/          # openapi.yaml
├── frontend/            # Application Vue.js
│   ├── Dockerfile
│   ├── src/
│   │   ├── views/       # Vues (authentication, dashboard, share)
│   │   ├── stores/      # Stores Pinia (auth, crypto, documents, share)
│   │   ├── router/      # Configuration des routes
│   │   └── utils/       # Utilitaires (fileEncryption)
│   ├── package.json
│   └── vite.config.ts
├── database/            # Configuration MySQL
│   ├── Dockerfile
│   └── schemas.sql      # Schéma de base de données
├── minio/              # Configuration MinIO (stockage S3)
│   └── Dockerfile
├── docs/               # Documentation
│   └── dossier-technique.md
├── .github/
│   └── workflows/      # CI/CD GitHub Actions
├── docker-compose.yml  # Orchestration des services
├── JOURNAL.md         # Journal de développement détaillé
├── .env               # Variables d'environnement
└── README.md
```

## Hot Reload (Développement)

Le projet est configuré pour le hot reload :
- **Frontend** : Les modifications dans `frontend/src/` sont détectées automatiquement (polling activé pour Docker)
- **Backend** : Les modifications dans `backend/app.py` rechargent Flask automatiquement

Pas besoin de rebuild après chaque modification !

## Tests & CI/CD

Le projet inclut une CI GitHub Actions complète qui :
- Build tous les conteneurs Docker
- Lance tous les services
- Teste l'enregistrement et la validation des mots de passe
- Teste la connexion à la base de données
- Teste l'authentification (login/token/2FA)
- Teste l'upload de documents chiffrés
- Teste la récupération de la liste de documents
- Teste les informations utilisateur
- Teste la génération et récupération de clés publiques RSA
- Teste les protections d'authentification
- Teste les endpoints de partage
- Linting Python et TypeScript

La CI se déclenche automatiquement sur les pushs et pull requests vers `main`, `import_export_cles`, `development`, `ci_cd`, et `docs-archi-yoda`.

Pour voir les résultats : https://github.com/tit6/YODA/actions

## Sécurité

### Architecture Zero-Knowledge

**Principe fondamental** : Le serveur ne voit jamais vos données en clair.

- **Chiffrement côté client** : Tous les documents sont chiffrés dans votre navigateur avant envoi
- **Clés locales uniquement** : Vos clés privées ne quittent jamais votre appareil
- **DEK par document** : Chaque document a sa propre clé de chiffrement (Data Encryption Key)
- **Protection RSA** : Les DEK sont chiffrées avec votre clé publique RSA-4096
- **Partage sécurisé** : Les partages utilisent des SEK (Share Encryption Key) générées côté serveur

### Fonctionnalités de sécurité implémentées

- **Chiffrement AES-256-GCM** : Chiffrement authentifié côté client avec IV unique
- **RSA-4096** : Paires de clés asymétriques générées localement
- **Authentification JWT** : Tokens signés avec clé secrète serveur
- **2FA TOTP obligatoire** : Authentification à deux facteurs avec Google Authenticator
- **Secret 2FA chiffré** : Stockage chiffré avec APP_MASTER_KEY (AES-256)
- **Hachage bcrypt** : Mots de passe hashés avec salt automatique
- **Politique de mots de passe forte** : Longueur et complexité imposées
- **Hash SHA-256** : Vérification d'intégrité des documents
- **Logs d'audit** : Tracking complet avec IP, timestamp, action
- **Protection anti-brute force** : Logs des tentatives de connexion échouées
- **Export/Import sécurisé** : Clés privées exportées chiffrées avec passphrase

### Configuration de sécurité

**IMPORTANT** : Les credentials par défaut sont pour le développement uniquement.

En production :
- Changez tous les mots de passe dans `.env`
- Régénérez `APP_MASTER_KEY` (clé AES-256 auto-générée au premier lancement)
- Configurez des credentials MinIO forts
- Utilisez HTTPS avec certificats valides
- Configurez un reverse proxy (nginx/traefik)
- Limitez l'exposition des ports (uniquement frontend en production)
- Activez le rate limiting sur les endpoints sensibles
- Configurez les CORS correctement
- Sauvegardez régulièrement la base de données

## API Endpoints

### Authentification
- `POST /api/register` - Inscription avec validation email
- `POST /api/login` - Connexion (retourne token temporaire si 2FA activé)
- `POST /api/verify-2fa` - Vérification du code TOTP (retourne token final)
- `POST /api/a2f` - Activer/désactiver 2FA
- `GET /api/statue_a2f` - Vérifier le statut 2FA

### Utilisateur
- `GET /api/name_user` - Informations utilisateur (nom, prénom, email)
- `GET /api/statue_session` - Statut de la session JWT
- `POST /api/change_password` - Changer le mot de passe
- `GET /api/user/public-key` - Récupérer la clé publique RSA
- `POST /api/user/public-key` - Sauvegarder la clé publique RSA

### Documents
- `POST /api/documents/upload` - Upload document chiffré (DEK wrappée, IV, hash)
- `GET /api/documents/list` - Liste des documents avec métadonnées
- `POST /api/documents/download` - Télécharger document + DEK wrappée
- `DELETE /api/documents/<id>` - Supprimer un document

### Partage sécurisé
- `POST /api/share/upload` - Créer un partage avec SEK
- `GET /api/share/list` - Liste des documents partagés par l'utilisateur
- `POST /api/share/switch` - Activer/désactiver un partage
- `POST /api/share/name_file` - Récupérer métadonnées d'un partage
- `POST /api/share/download` - Télécharger via lien de partage public

### Monitoring
- `GET /api/health` - Health check du backend
- `GET /api/db-test` - Test de connexion MySQL

## Documentation complète

- **Dossier technique** : `docs/dossier-technique.md` - Architecture détaillée, cryptographie, API
- **Journal de développement** : `JOURNAL.md` - Historique complet du projet
- **OpenAPI Spec** : `backend/static/openapi.yaml` - Spécification complète de l'API

## Contribution

1. Créer une branche : `git checkout -b feature/ma-feature`
2. Commit : `git commit -m 'Ajout de ma feature'`
3. Push : `git push origin feature/ma-feature`
4. Créer une Pull Request

## Licence

Voir le fichier [LICENSE](LICENSE)
