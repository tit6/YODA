from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
from module.config import APP_MASTER_KEY


def aes256_encrypt(data: bytes) -> str:
    key = APP_MASTER_KEY
    # 1) Générer un IV aléatoire de 16 octets
    iv = get_random_bytes(16)

    # 2) Créer le cipher AES-256 en mode CBC
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)

    # 3) Ajouter le padding et chiffrer
    ciphertext = cipher.encrypt(pad(data, AES.block_size))

    # 4) Mettre IV + ciphertext dans le résultat
    iv_and_ciphertext = iv + ciphertext

    # Optionnel : encoder en base64 pour stockage/transport
    return base64.b64encode(iv_and_ciphertext).decode("utf-8")

def aes256_decrypt(b64_data: str) -> bytes:
    key = APP_MASTER_KEY
    # 1) Décoder le base64
    iv_and_ciphertext = base64.b64decode(b64_data)

    # 2) Récupérer IV (16 octets) + ciphertext
    iv = iv_and_ciphertext[:16]
    ciphertext = iv_and_ciphertext[16:]

    # 3) Créer le cipher et déchiffrer
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext

