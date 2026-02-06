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

        // Stocker aussi la clé publique en PEM pour la synchroniser plus tard
        const publicKeySpki = await crypto.subtle.exportKey("spki", keyPair.publicKey);
        const publicKeyPem = exportPublicKeyToPem(publicKeySpki);
        await saveKeyToDatabase("publickey_pem", publicKeyPem);

        return true;
    },

    SyncPublicKeyToBackend: async (): Promise<boolean> => {
        // Vérifier si une clé privée existe
        const privateKeyJWK = await getKeyFromDatabase("privatekey");
        if (!privateKeyJWK) {
            console.log('No private key found');
            return false;
        }

        // Récupérer la clé publique PEM stockée
        let publicKeyPem = await getKeyFromDatabase("publickey_pem");

        // Si pas de PEM stocké, le générer depuis la clé privée
        if (!publicKeyPem) {
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

            const publicKeySpki = await crypto.subtle.exportKey("spki", publicKeyObject);
            publicKeyPem = exportPublicKeyToPem(publicKeySpki);
            await saveKeyToDatabase("publickey_pem", publicKeyPem);
        }

        // Envoyer au backend
        const token = localStorage.getItem('auth_token');
        if (!token) {
            console.log('No token found');
            return false;
        }

        try {
            const response = await fetch('/api/user/public-key', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ public_key: publicKeyPem })
            });

            if (!response.ok) {
                const data = await response.json();
                // Si la clé existe déjà (409), c'est OK
                if (response.status === 409) {
                    console.log('Public key already exists in backend');
                    return true;
                }
                console.error('Failed to save public key to backend:', data);
                return false;
            }

            console.log('Public key synced to backend');
            return true;
        } catch (e) {
            console.error('Error saving public key:', e);
            return false;
        }
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
    GenerateDek: async (): Promise<CryptoKey> => {
        const key = await crypto.subtle.generateKey(
            { name: "AES-GCM", length: 256 },
            true,  // extractable
            ["encrypt", "decrypt"]
        );

        return key;
    },

    /**
     * Chiffre un fichier avec une DEK et récupère la clé publique RSA du serveur
     *
     * @param {File} file - Fichier à chiffrer
     * @returns {Promise<EncryptedFileResult>}
     */
    EncryptFile: async (file: File): Promise<{
        encryptedData: ArrayBuffer,
        dekEncrypted: string,
        iv: string,
        sha256: string
    }> => {
        // 1. Lire le fichier
        const fileBuffer = await file.arrayBuffer();

        // 2. Calculer le SHA-256 du fichier original
        const sha256Hash = await crypto.subtle.digest("SHA-256", fileBuffer);
        const sha256 = arrayBufferToBase64(sha256Hash);

        // 3. Générer une DEK (Data Encryption Key)
        const dek = await DEK.GenerateDek();

        // 4. Générer un IV aléatoire
        const iv = crypto.getRandomValues(new Uint8Array(12));

        // 5. Chiffrer le fichier avec AES-GCM
        const encryptedData = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            dek,
            fileBuffer
        );

        // 6. Récupérer la clé publique RSA de l'utilisateur depuis le backend
        const publicKeyPem = await fetchPublicKeyFromBackend();

        // 7. Importer la clé publique
        const publicKey = await importPublicKeyFromPem(publicKeyPem);

        // 8. Exporter la DEK en raw
        const dekRaw = await crypto.subtle.exportKey("raw", dek);

        // 9. Chiffrer la DEK avec la clé publique RSA
        const dekEncryptedBuffer = await crypto.subtle.encrypt(
            { name: "RSA-OAEP" },
            publicKey,
            dekRaw
        );

        return {
            encryptedData,
            dekEncrypted: arrayBufferToBase64(dekEncryptedBuffer),
            iv: arrayBufferToBase64(iv),
            sha256
        };
    },

    /**
     * Déchiffre un fichier avec la clé privée locale
     *
     * @param {ArrayBuffer} encryptedData - Données chiffrées
     * @param {string} dekEncrypted - DEK chiffrée en base64
     * @param {string} ivBase64 - IV en base64
     * @returns {Promise<ArrayBuffer>}
     */
    DecryptFile: async (
        encryptedData: ArrayBuffer,
        dekEncrypted: string,
        ivBase64: string
    ): Promise<ArrayBuffer> => {
        // 1. Déchiffrer la DEK avec la clé privée RSA locale
        const dekRaw = await PrivateKey.DecryptDek(dekEncrypted);

        // 2. Importer la DEK
        const dek = await crypto.subtle.importKey(
            "raw",
            dekRaw,
            { name: "AES-GCM", length: 256 },
            false,
            ["decrypt"]
        );

        // 3. Convertir l'IV depuis base64
        const iv = Uint8Array.from(atob(ivBase64), c => c.charCodeAt(0));

        // 4. Déchiffrer le fichier
        const decryptedData = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: iv },
            dek,
            encryptedData
        );

        return decryptedData;
    }
}

/**
 * Récupère la clé publique RSA de l'utilisateur depuis le backend
 */
async function fetchPublicKeyFromBackend(): Promise<string> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('/api/user/public-key', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error('Impossible de récupérer la clé publique');
    }

    const data = await response.json();
    return data.data.public_key;
}

/**
 * Importe une clé publique RSA depuis le format PEM
 */
async function importPublicKeyFromPem(pem: string): Promise<CryptoKey> {
    // Retirer les headers/footers PEM
    const pemContents = pem
        .replace(/-----BEGIN PUBLIC KEY-----/, '')
        .replace(/-----END PUBLIC KEY-----/, '')
        .replace(/\s/g, '');

    // Décoder le base64
    const binaryDer = Uint8Array.from(atob(pemContents), c => c.charCodeAt(0));

    // Importer la clé
    return await crypto.subtle.importKey(
        "spki",
        binaryDer.buffer,
        { name: "RSA-OAEP", hash: "SHA-256" },
        false,
        ["encrypt"]
    );
}

/**
 * Exporte une clé publique RSA au format PEM
 */
function exportPublicKeyToPem(publicKeySpki: ArrayBuffer): string {
    const b64 = arrayBufferToBase64(publicKeySpki);
    // Formater en PEM avec retours à la ligne tous les 64 caractères
    const pem = b64.match(/.{1,64}/g)?.join('\n') || b64;
    return `-----BEGIN PUBLIC KEY-----\n${pem}\n-----END PUBLIC KEY-----`;
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
    },

    // Import et déchiffrement de la clé privée
    importPrivateKey: async (fileContent: string, passphrase: string): Promise<boolean> => {
        try {
            // 1. Parse du fichier JSON
            const importData = JSON.parse(fileContent);

            // Validation du format
            if (!importData.version || !importData.wrappedPrivateKey || !importData.salt || !importData.iv) {
                throw new Error("Format de fichier invalide");
            }

            // 2. Conversion des données base64
            const wrappedPrivateKey = base64ToArrayBuffer(importData.wrappedPrivateKey);
            const salt = base64ToArrayBuffer(importData.salt);
            const iv = base64ToArrayBuffer(importData.iv);

            // 3. Dérivation de la KEK depuis la passphrase
            const { kek } = await PrivateKeyExport.deriveKeyFromPassphrase(
                passphrase,
                new Uint8Array(salt)
            );

            // 4. Déchiffrement de la clé privée
            const privateKeyPKCS8 = await crypto.subtle.decrypt(
                { name: "AES-GCM", iv: new Uint8Array(iv) },
                kek,
                wrappedPrivateKey
            );

            // 5. Import de la clé privée déchiffrée
            const privateKeyObject = await crypto.subtle.importKey(
                "pkcs8",
                privateKeyPKCS8,
                { name: "RSA-OAEP", hash: "SHA-256" },
                true,
                ["decrypt"]
            );

            // 6. Vérification de l'empreinte de la clé publique (si disponible)
            if (importData.publicKeyFingerprint) {
                const privateKeyJWK = await crypto.subtle.exportKey("jwk", privateKeyObject);
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
                const computedFingerprint = arrayBufferToBase64(publicKeyHash);

                if (computedFingerprint !== importData.publicKeyFingerprint) {
                    throw new Error("L'empreinte de la clé ne correspond pas");
                }
            }

            // 7. Sauvegarde dans IndexedDB
            const privateKeyJWK = await crypto.subtle.exportKey("jwk", privateKeyObject);
            await saveKeyToDatabase("privatekey", privateKeyJWK);

            // 8. Sauvegarde de la clé publique au format PEM
            const privateKeyJWKForPublic = await crypto.subtle.exportKey("jwk", privateKeyObject);
            const publicKeyJWK = { ...privateKeyJWKForPublic };
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

            const publicKeySpki = await crypto.subtle.exportKey("spki", publicKeyObject);
            const publicKeyPem = exportPublicKeyToPem(publicKeySpki);
            await saveKeyToDatabase("publickey_pem", publicKeyPem);

            return true;
        } catch (error) {
            console.error("Erreur lors de l'import:", error);
            throw error;
        }
    }
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

