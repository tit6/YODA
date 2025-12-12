// Vérification que l'API cryptographique est disponible (HTTPS requis)
if (!window.crypto || !window.crypto.subtle) {
    alert('Utiliser https ou localhost pour utiliser cette application sinon ça marche pas.');
}

// Initialisation de la base de données IndexedDB
const dbRequest = indexedDB.open('PrivateDatabase', 1);

// Promesse pour attendre l'ouverture complète de la base de données
const dbReady: Promise<IDBDatabase> = new Promise((resolve, reject) => {
    // Création du schéma de la base (première ouverture)
    dbRequest.onupgradeneeded = () => {
        const db = dbRequest.result;
        if (!db.objectStoreNames.contains('keys')) {
            db.createObjectStore('keys', { keyPath: 'id' });
        }
    };

    // Base de données ouverte avec succès
    dbRequest.onsuccess = () => {
        resolve(dbRequest.result);
    };

    // Erreur lors de l'ouverture
    dbRequest.onerror = () => {
        reject(dbRequest.error);
    };
});

/**
 * Sauvegarde une clé dans IndexedDB
 */
async function saveKeyToDatabase(keyId: string, keyData: any): Promise<void> {
    const db = await dbReady;
    const transaction = db.transaction('keys', 'readwrite');
    const store = transaction.objectStore('keys');

    return new Promise((resolve, reject) => {
        const request = store.put({ id: keyId, key: keyData });
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Récupère une clé depuis IndexedDB
 */
async function getKeyFromDatabase(keyId: string): Promise<any> {
    const db = await dbReady;
    const transaction = db.transaction('keys', 'readonly');
    const store = transaction.objectStore('keys');

    return new Promise((resolve, reject) => {
        const request = store.get(keyId);
        request.onsuccess = () => resolve(request.result?.key);
        request.onerror = () => reject(request.error);
    });
}

export const PrivateKey = {
    GeneratePrivateKey: async (): Promise<boolean> => {
        // Génération de la paire de clés RSA
        const keyPair = await crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]), // 65537
                hash: "SHA-256"
            },
            true,  // extractable
            ["encrypt", "decrypt"]
        );

        // Export de la clé privée au format JWK (pour IndexedDB)
        const privateKeyJWK = await crypto.subtle.exportKey("jwk", keyPair.privateKey);

        // Sauvegarde dans IndexedDB
        await saveKeyToDatabase("privatekey", privateKeyJWK);

        // TODO: Envoyer la clé publique au backend
        return true;
    },

    GetPrivateKey: async (): Promise<JsonWebKey> => {
        return await getKeyFromDatabase("privatekey");
    },

    DecryptDek: async (encryptedDek: string): Promise<ArrayBuffer> => {
        // Récupération de la clé privée
        const privateKeyJWK = await PrivateKey.GetPrivateKey();

        // Réimportation de la clé depuis JWK pour utilisation
        const privateKey = await crypto.subtle.importKey(
            "jwk",
            privateKeyJWK,
            { name: "RSA-OAEP", hash: "SHA-256" },
            false,
            ["decrypt"]
        );

        // Conversion Base64 -> Uint8Array
        const encryptedBytes = Uint8Array.from(atob(encryptedDek), c => c.charCodeAt(0));

        // Déchiffrement RSA-OAEP
        return await crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            privateKey,
            encryptedBytes
        );
    }
}

export const DEK = {
    GenerateDek: async (): Promise<ArrayBuffer> => {
        const key = await crypto.subtle.generateKey(
            { name: "AES-GCM", length: 256 },
            true,  // extractable
            ["encrypt", "decrypt"]
        );

        return await crypto.subtle.exportKey("raw", key);
    },

    /**
     * Chiffre un fichier avec une DEK
     *
     * TODO: Implémenter le chiffrement du fichier avec la DEK générée
     * puis chiffrer la DEK avec la clé publique du backend
     *
     * @param {any} file - Fichier à chiffrer
     * @returns {Promise<void>}
     */
    EncryptFile: async (file: any): Promise<void> => {
        // À implémenter
        return;
    }
}

function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
    const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]!);
    }
    return btoa(binary);
}

export const PrivateKeyExport = {
    deriveKeyFromPassphrase: async (
        passphrase: string,
        salt: Uint8Array
    ): Promise<{ kek: CryptoKey, params: any }> => {
        const encoder = new TextEncoder();

        // Import de la passphrase comme clé de base
        const passphraseKey = await crypto.subtle.importKey(
            "raw",
            encoder.encode(passphrase),
            "PBKDF2",
            false,
            ["deriveBits", "deriveKey"]
        );

        // Dérivation de la KEK (Key Encryption Key) avec PBKDF2
        const kek = await crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: salt.buffer as ArrayBuffer,
                iterations: 600000,
                hash: "SHA-256"
            },
            passphraseKey,
            { name: "AES-GCM", length: 256 },
            false,  // non extractable
            ["encrypt", "decrypt"]
        );

        return {
            kek,
            params: {
                algorithm: "PBKDF2",
                iterations: 600000,
                hash: "SHA-256"
            }
        };
    },

    // Export et chiffrement de la clé privée
    exportPrivateKey: async (passphrase: string): Promise<string> => {
        // 1. Récupération de la clé privée depuis IndexedDB
        const db = await dbReady;
        const transaction = db.transaction('keys', 'readonly');
        const store = transaction.objectStore('keys');

        const privateKeyJWK = await new Promise<any>((resolve, reject) => {
            const request = store.get("privatekey");
            request.onsuccess = () => resolve(request.result?.key);
            request.onerror = () => reject(request.error);
        });

        if (!privateKeyJWK) {
            throw new Error("Clé privée introuvable");
        }

        // 2. Export de la clé privée en format PKCS#8
        const privateKeyObject = await crypto.subtle.importKey(
            "jwk",
            privateKeyJWK,
            { name: "RSA-OAEP", hash: "SHA-256" },
            true,
            ["decrypt"]
        );

        const privateKeyPKCS8 = await crypto.subtle.exportKey("pkcs8", privateKeyObject);

        // 3. Génération du sel pour la dérivation
        const salt = crypto.getRandomValues(new Uint8Array(16));

        // 4. Dérivation de la KEK depuis la passphrase
        const { kek, params } = await PrivateKeyExport.deriveKeyFromPassphrase(passphrase, salt);

        // 5. Génération de l'IV pour AES-GCM
        const iv = crypto.getRandomValues(new Uint8Array(12));

        // 6. Chiffrement de la clé privée avec AES-256-GCM
        const encryptedPrivateKey = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            kek,
            privateKeyPKCS8
        );

        // 7. Calcul de l'empreinte SHA-256 de la clé publique (pour vérification)
        // On récupère la clé publique associée
        const publicKeyJWK = { ...privateKeyJWK };
        delete publicKeyJWK.d;
        delete publicKeyJWK.p;
        delete publicKeyJWK.q;
        delete publicKeyJWK.dp;
        delete publicKeyJWK.dq;
        delete publicKeyJWK.qi;
        publicKeyJWK.key_ops = ["encrypt"];

        const publicKeyObject = await crypto.subtle.importKey(
            "jwk",
            publicKeyJWK,
            { name: "RSA-OAEP", hash: "SHA-256" },
            true,
            ["encrypt"]
        );

        const publicKeyBuffer = await crypto.subtle.exportKey("spki", publicKeyObject);
        const publicKeyHash = await crypto.subtle.digest("SHA-256", publicKeyBuffer);

        // 8. Création du fichier JSON
        const exportData = {
            version: "1.0",
            exportDate: new Date().toISOString(),
            wrappedPrivateKey: arrayBufferToBase64(encryptedPrivateKey),
            salt: arrayBufferToBase64(salt),
            iv: arrayBufferToBase64(iv),
            kdfParams: params,
            publicKeyFingerprint: arrayBufferToBase64(publicKeyHash),
            algorithm: "RSA-OAEP-2048",
            encryption: "AES-256-GCM"
        };

        return JSON.stringify(exportData, null, 2);
    },

    // Téléchargement du fichier d'export
    downloadExportFile: (jsonContent: string) => {
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `privatekey-backup-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

