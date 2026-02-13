from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from module.db import execute_write, fetch_all, fetch_one


def get_folder(user_id: int, folder_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère un dossier par ID, uniquement si il appartient à l'utilisateur.

    Utilisé par:
    - POST /api/documents/upload (validation folder_id)
    - GET  /api/documents/list   (validation folder_id)
    - POST /api/documents/folders/create (validation parent_id)
    - DELETE /api/documents/folders/delete/<folder_id> (ownership check)

    Sortie:
    - dict (ligne SQL: id, id_users, nom, parent_id, created_at) ou None si introuvable / non autorisé.
    """
    return fetch_one(
        "SELECT id, id_users, nom, parent_id, created_at FROM folders WHERE id = %s AND id_users = %s",
        (folder_id, user_id),
    )


def list_child_folders(user_id: int, parent_id: Optional[int]) -> List[Dict[str, Any]]:
    """
    Liste les sous-dossiers directs d'un dossier (ou la racine si parent_id=None).

    Utilisé par:
    - GET /api/documents/list (pour renvoyer `data.folders` du dossier courant)

    Entrée:
    - parent_id: None => racine du user (parent_id IS NULL), sinon ID du dossier parent

    Sortie:
    - Liste de dicts au format attendu par le frontend: {id, name, created_at(ISO|None)}
    """
    if parent_id is None:
        rows = fetch_all(
            "SELECT id, nom, created_at FROM folders WHERE id_users = %s AND parent_id IS NULL ORDER BY nom ASC",
            (user_id,),
        )
    else:
        rows = fetch_all(
            "SELECT id, nom, created_at FROM folders WHERE id_users = %s AND parent_id = %s ORDER BY nom ASC",
            (user_id, parent_id),
        )

    folders: List[Dict[str, Any]] = []
    for r in rows:
        created_at = r.get("created_at")
        if created_at is None:
            created_at_value = None
        elif hasattr(created_at, "isoformat"):
            created_at_value = created_at.isoformat()
        else:
            created_at_value = str(created_at)
        folders.append(
            {
                "id": int(r["id"]),
                "name": r.get("nom") or "",
                "created_at": created_at_value,
            }
        )
    return folders


def create_folder(user_id: int, name: str, parent_id: Optional[int]) -> int:
    """
    Crée un dossier pour l'utilisateur (parent_id peut être None => racine).

    Utilisé par:
    - POST /api/documents/folders/create

    Sécurité:
    - Si parent_id est fourni, il doit appartenir au même user (sinon PermissionError).

    Sortie:
    - ID (int) du dossier créé.
    """
    name = (name or "").strip()
    if not name:
        raise ValueError("Nom de dossier manquant")

    if parent_id is not None and get_folder(user_id, int(parent_id)) is None:
        # Important: interdit de créer un dossier sous un parent d'un autre user.
        raise PermissionError("Parent introuvable ou non autorisé")

    _, folder_id = execute_write(
        "INSERT INTO folders (id_users, nom, parent_id) VALUES (%s, %s, %s)",
        (user_id, name, parent_id),
    )
    return int(folder_id)


def build_breadcrumb(user_id: int, folder_id: Optional[int]) -> List[Dict[str, Any]]:
    """
    Construit le fil d'Ariane (breadcrumb) d'un dossier: racine -> dossier courant.

    Utilisé par:
    - GET /api/documents/list (pour renvoyer `data.breadcrumb`)

    Sortie:
    - [] si folder_id est None (racine)
    - sinon liste [{id, name}, ...] dans l'ordre racine -> courant
    """
    if folder_id is None:
        return []

    crumbs: List[Dict[str, Any]] = []
    current: Optional[int] = int(folder_id)
    seen: Set[int] = set()

    while current is not None and current not in seen:
        seen.add(current)
        row = fetch_one(
            "SELECT id, nom, parent_id FROM folders WHERE id_users = %s AND id = %s",
            (user_id, current),
        )
        if row is None:
            break
        crumbs.append({"id": int(row["id"]), "name": row.get("nom") or ""})
        current = row.get("parent_id")

    crumbs.reverse()
    return crumbs

def get_descendant_folder_ids(user_id: int, folder_id: int, include_self: bool = True) -> List[int]:
    """
    Retourne les IDs de tous les sous-dossiers (récursif) d'un dossier.

    Utilisé par:
    - DELETE /api/documents/folders/delete/<folder_id> (suppression des docs du sous-arbre)

    Sortie:
    - Liste d'IDs (int). include_self=True inclut folder_id dans la liste.
    """
    if get_folder(user_id, folder_id) is None:
        raise PermissionError("Dossier introuvable ou non autorisé")

    rows = fetch_all("SELECT id, parent_id FROM folders WHERE id_users = %s", (user_id,))
    children: Dict[Optional[int], List[int]] = {}
    for r in rows:
        pid = r.get("parent_id")
        children.setdefault(pid, []).append(int(r["id"]))

    result: List[int] = [int(folder_id)] if include_self else []
    stack: List[int] = [int(folder_id)]
    seen: Set[int] = {int(folder_id)}

    while stack:
        current = stack.pop()
        for cid in children.get(current, []):
            if cid in seen:
                continue
            seen.add(cid)
            result.append(cid)
            stack.append(cid)

    return result
