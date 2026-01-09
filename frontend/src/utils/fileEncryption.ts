/**
 * Utilitaires pour le chiffrement de fichiers par chunks
 * Gère les gros fichiers sans Out of Memory
 */

/**
 * Calcule le SHA-256 d'un fichier en le lisant par chunks
 */
export async function calculateSHA256InChunks(file: File): Promise<ArrayBuffer> {
    const CHUNK_SIZE = 64 * 1024 * 1024; // 64 MB
    const chunks = Math.ceil(file.size / CHUNK_SIZE);

    // On doit lire tout le fichier pour calculer le hash
    let offset = 0;
    const fullData = new Uint8Array(file.size);

    for (let i = 0; i < chunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);
        const chunkData = new Uint8Array(await chunk.arrayBuffer());
        fullData.set(chunkData, offset);
        offset += chunkData.length;
    }

    return await crypto.subtle.digest('SHA-256', fullData);
}

/**
 * Chiffre un fichier par chunks et retourne le résultat en base64 par morceaux
 */
export async function encryptFileInChunks(
    file: File,
    dek: CryptoKey,
    iv: Uint8Array,
    onProgress?: (progress: number) => void
): Promise<Blob> {
    const CHUNK_SIZE = 64 * 1024 * 1024; // 64 MB par chunk
    const encryptedChunks: Blob[] = [];
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);
        const chunkBuffer = await chunk.arrayBuffer();

        // Pour AES-GCM, on utilise un IV unique par chunk
        const chunkIv = new Uint8Array(12);
        chunkIv.set(iv);
        // Ajouter l'index du chunk aux derniers octets
        const chunkIndex = new DataView(chunkIv.buffer);
        chunkIndex.setUint32(8, i, false);

        const encryptedChunk = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: chunkIv },
            dek,
            chunkBuffer
        );

        encryptedChunks.push(new Blob([encryptedChunk]));

        if (onProgress) {
            const progress = Math.floor((i + 1) / totalChunks * 100);
            onProgress(progress);
        }
    }

    // Retourner un Blob combiné
    return new Blob(encryptedChunks);
}

/**
 * Déchiffre un fichier par chunks
 */
export async function decryptFileInChunks(
    encryptedBlob: Blob,
    dek: CryptoKey,
    iv: Uint8Array
): Promise<Blob> {
    const CHUNK_SIZE = 64 * 1024 * 1024 + 16; // 64 MB + 16 bytes pour le tag AES-GCM
    const decryptedChunks: Blob[] = [];
    const totalChunks = Math.ceil(encryptedBlob.size / CHUNK_SIZE);

    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, encryptedBlob.size);
        const chunk = encryptedBlob.slice(start, end);
        const chunkBuffer = await chunk.arrayBuffer();

        // Reconstruire le même IV que lors du chiffrement
        const chunkIv = new Uint8Array(12);
        chunkIv.set(iv);
        const chunkIndex = new DataView(chunkIv.buffer);
        chunkIndex.setUint32(8, i, false);

        const decryptedChunk = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: chunkIv },
            dek,
            chunkBuffer
        );

        decryptedChunks.push(new Blob([decryptedChunk]));
    }

    return new Blob(decryptedChunks);
}

/**
 * Convertit un Blob en base64 par morceaux pour éviter Out of Memory
 */
export async function blobToBase64InChunks(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64 = reader.result as string;
            // Retirer le préfixe data:...;base64,
            const base64Data = base64.split(',')[1];
            resolve(base64Data || '');
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}
