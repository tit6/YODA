# YODA - Coffre-fort Numérique

Application de coffre-fort numérique sécurisé avec stockage de fichiers chiffrés.

## 🏗️ Architecture

- **Frontend** : Vue.js 3 + TypeScript + Vite
- **Backend** : Python Flask + API REST
- **Database** : MySQL 8.0
- **Storage** : MinIO (stockage d'objets compatible S3)
- **Containerisation** : Docker + Docker Compose

## 📋 Prérequis

- Docker Desktop
- Git

## 🚀 Installation

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

## 🎯 Accès aux services

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

## 🛠️ Commandes utiles

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

## 📁 Structure du projet

```
YODA/
├── backend/              # API Flask Python
│   ├── Dockerfile
│   ├── app.py           # Point d'entrée
│   └── requirements.txt
├── frontend/            # Application Vue.js
│   ├── Dockerfile
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── database/            # Configuration MySQL
│   └── Dockerfile
├── minio/              # Configuration MinIO
│   └── Dockerfile
├── .github/
│   └── workflows/      # CI/CD GitHub Actions
│       ├── ci.yml
│       ├── docker-ci.yml
│       └── main.yml
├── docker-compose.yml  # Orchestration des services
├── .env               # Variables d'environnement
└── README.md
```

## 🔥 Hot Reload (Développement)

Le projet est configuré pour le hot reload :
- **Frontend** : Les modifications dans `frontend/src/` sont détectées automatiquement (polling activé pour Docker)
- **Backend** : Les modifications dans `backend/app.py` rechargent Flask automatiquement

Pas besoin de rebuild après chaque modification !

## 🧪 Tests & CI/CD

Le projet inclut une CI GitHub Actions qui :
- Build tous les conteneurs Docker
- Lance tous les services
- Teste les endpoints du backend
- Vérifie la connexion à la base de données
- Teste le frontend

La CI se déclenche automatiquement sur les pushs et pull requests vers `main`.

## 🔐 Sécurité

⚠️ **Important** : Les credentials par défaut sont pour le développement uniquement.

En production :
- Changez tous les mots de passe dans `.env`
- N'exposez pas les ports sensibles
- Utilisez HTTPS
- Activez le chiffrement MinIO

## 📝 API Endpoints

### Backend Flask

- `GET /coucou` - Test simple, retourne un message JSON
- `GET /db-test` - Test connexion MySQL, retourne la version de la base

## 🤝 Contribution

1. Créer une branche : `git checkout -b feature/ma-feature`
2. Commit : `git commit -m 'Ajout de ma feature'`
3. Push : `git push origin feature/ma-feature`
4. Créer une Pull Request

## 📄 Licence

Voir le fichier [LICENSE](LICENSE)