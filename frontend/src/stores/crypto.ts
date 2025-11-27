import {ref} from 'vue'

interface CryptoKeys {
    publicKey: CryptoKey | null;
    privateKey: CryptoKey | null;
}

const Crypto = {
    keys: ref<CryptoKeys>({
        publicKey: null,
        privateKey: null
    }),

    // Generate a new AES-256 key (DEK)
    async generateDEK(): Promise<CryptoKey> {
        return await window.crypto.subtle.generateKey(
            {
                name: "AES-GCM",
                length: 256
            },
            true, // extractable
            ["encrypt", "decrypt"]
        );
    },

    // Generate random IV
    generateIV(): Uint8Array {
        return window.crypto.getRandomValues(new Uint8Array(12));
    },

    // Encrypt file with DEK
    async encryptFile(file: File, dek: CryptoKey): Promise<{
        encryptedFile: ArrayBuffer,
        iv: Uint8Array,
        originalHash: ArrayBuffer
    }> {
        const iv = this.generateIV();
        const fileBuffer = await file.arrayBuffer();

        // Calculate original file hash
        const originalHash = await window.crypto.subtle.digest('SHA-256', fileBuffer);

        // Encrypt the file
        const encryptedFile = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            dek,
            fileBuffer
        );

        return {
            encryptedFile,
            iv,
            originalHash
        };
    },

    // Wrap (encrypt) the DEK with user's public RSA key
    async wrapDEK(dek: CryptoKey, publicKey: CryptoKey): Promise<ArrayBuffer> {
        return await window.crypto.subtle.wrapKey(
            "raw",
            dek,
            publicKey,
            {
                name: "RSA-OAEP"
            }
        );
    },

    // Unwrap (decrypt) the DEK with user's private RSA key
    async unwrapDEK(wrappedDek: ArrayBuffer, privateKey: CryptoKey): Promise<CryptoKey> {
        return await window.crypto.subtle.unwrapKey(
            "raw",
            wrappedDek,
            privateKey,
            {
                name: "RSA-OAEP"
            },
            {
                name: "AES-GCM",
                length: 256
            },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // Decrypt file using DEK
    decryptFile: async function (encryptedFile: ArrayBuffer, dek: CryptoKey, iv: Uint8Array): Promise<ArrayBuffer> {
        return await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            dek,
            encryptedFile
        );
    },

    // Import RSA public key
    async importPublicKey(publicKeyData: JsonWebKey): Promise<void> {
        this.keys.value.publicKey = await window.crypto.subtle.importKey(
            "jwk",
            publicKeyData,
            {
                name: "RSA-OAEP",
                hash: "SHA-256"
            },
            true,
            ["wrapKey"]
        );
    },

    // Import RSA private key
    async importPrivateKey(privateKeyData: JsonWebKey): Promise<void> {
        this.keys.value.privateKey = await window.crypto.subtle.importKey(
            "jwk",
            privateKeyData,
            {
                name: "RSA-OAEP",
                hash: "SHA-256"
            },
            true,
            ["unwrapKey"]
        );
    }
}

export default Crypto;