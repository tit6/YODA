import os
import base64
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv
from module.middleware import auth_middleware

from routes import register_blueprints

# Chemin fixe : fichier .env situé à côté de app.py (monté dans le conteneur)
ENV_PATH = Path(__file__).resolve().parent / ".env"

def ensure_master_key():
    """
    Vérifie le .env (priorité à la racine du projet).
    - Si APP_MASTER_KEY est absente ou vide → génère une clé AES-256 et met à jour le fichier .env
    - Sinon → ne fait rien
    Dans tous les cas, affiche ce qu'il fait.
    """
    env_path = ENV_PATH
    load_dotenv(env_path if env_path.exists() else None)
    print(f"[INFO] .env utilisé : {env_path}")

    current_key = (os.getenv("APP_MASTER_KEY") or "").strip()

    # Lire le fichier brut (s'il n'existe pas, on part d'une liste vide)
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []

    # Si la clé est absente ou vide → on doit générer
    if not current_key:
        print("[INFO] APP_MASTER_KEY absente ou vide → génération d'une clé AES-256...")

        new_key = base64.b64encode(os.urandom(32)).decode()

        # Réécriture du .env en modifiant la ligne si elle existe
        new_lines = [line for line in lines if not line.strip().startswith("APP_MASTER_KEY=")]
        new_lines.append(f"APP_MASTER_KEY={new_key}")

        # Écrire le fichier mis à jour (création si nécessaire)
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        # Mettre à jour l'environnement courant (pour ce run) et le cache de config, si présent
        os.environ["APP_MASTER_KEY"] = new_key
        try:
            import module.config as config
            config.APP_MASTER_KEY = base64.b64decode(new_key)
        except Exception:
            pass

        print("[OK] APP_MASTER_KEY écrite dans le .env")
        print(f"[KEY] {new_key}")
        return new_key

    else:
        # La clé existe déjà → rien à faire
        print("[INFO] APP_MASTER_KEY détectée → aucune modification nécessaire.")
        print(f"[KEY] {current_key}")
        return current_key


def create_app():
    ensure_master_key()
    app = Flask(__name__)
    app.before_request(auth_middleware)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
