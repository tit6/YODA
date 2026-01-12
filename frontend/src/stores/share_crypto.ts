import { defineStore } from 'pinia'
import { useDocumentsStore} from '@/stores/documents'
import { DEK, PrivateKey } from '@/stores/crypto'
import { decryptFileInChunks, encryptFileInChunks, blobToBase64InChunks } from '@/utils/fileEncryption'


export const useShareCryptoStore = defineStore('share_crypto', {
  state: () => ({
    loading: false,
    error: ''
  }),
  actions: {
    async share_document(document_name: string, email: string, time: string, number_of_accesses: number | null, password: string) {
      // recupe share link from backend
        this.loading = true
        this.error = ''
        try {
            const documentsStore = useDocumentsStore()

            const result = await documentsStore.downloadDocument(document_name)
            if (!result) {
            return
            }

            console.log('Document téléchargé pour le partage:', result)
            
             // Déchiffrer la DEK avec la clé privée
            const privateKeyJWK = await PrivateKey.GetPrivateKey()
            console.log('Clé privée RSA (JWK):', privateKeyJWK)
            const privateKey = await crypto.subtle.importKey(
            "jwk",
            privateKeyJWK,
            { name: "RSA-OAEP", hash: "SHA-256" },
            false,
            ["decrypt"]
            )

            const dekEncryptedBytes = Uint8Array.from(atob(result.dekEncrypted), c => c.charCodeAt(0))
            const dekRaw = await crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            privateKey,
            dekEncryptedBytes
            )

            // Importer la DEK
            const dek = await crypto.subtle.importKey(
            "raw",
            dekRaw,
            { name: "AES-GCM", length: 256 },
            false,
            ["decrypt"]
            )

            // Convertir l'IV
            const iv = Uint8Array.from(atob(result.iv), c => c.charCodeAt(0))

            // Déchiffrer le fichier par chunks
            const decryptedBlob = await decryptFileInChunks(
            result.blob,
            dek,
            iv
            )


            console.log('Fichier déchiffré avec succès')
            console.log('decrupted file :', decryptedBlob)

            const decryptedFile = new File(
              [decryptedBlob],
              result.fileName,
              { type: result.blob.type || 'application/octet-stream' }
            )



            const newDek = await DEK.GenerateDek()
            const newIv = crypto.getRandomValues(new Uint8Array(12))

            const encryptedBlob = await encryptFileInChunks(
              decryptedFile,
              newDek,
              newIv
            )

            const newDekRaw = await crypto.subtle.exportKey("raw", newDek)
            const newDekBase64 = arrayBufferToBase64(newDekRaw)
            const newIvBase64 = arrayBufferToBase64(newIv)
            console.log('Nouvelle DEK (base64):', newDekBase64)
            console.log('Nouvel IV (base64):', newIvBase64)

            //download file
            //const downloadUrl = URL.createObjectURL(encryptedBlob)
            //const link = document.createElement('a')
            //link.href = downloadUrl
            //link.download = `encrypted-${result.fileName}`
            //document.body.appendChild(link)
            //link.click()
            //document.body.removeChild(link)
            //URL.revokeObjectURL(downloadUrl)

            console.log('Fichier rechiffré avec une nouvelle clé et un nouvel IV')

            
             //Upload vers le serveur
            const fileDataB64 = await blobToBase64InChunks(encryptedBlob)
            const uploadResult = await documentsStore.uploadDocument_shared({
              file_name: result.fileName,
              file_data: fileDataB64,
              dek_encrypted: newDekBase64,
              iv: newIvBase64,
              sha256: result.sha256,
              email: email,
              time: time,
              number_of_accesses: number_of_accesses,
            })
            if (!uploadResult) {
              throw new Error(documentsStore.error || 'Erreur lors de l\'upload')
            }
            
            
            return uploadResult.token


        }
        catch (err) {
            this.error = String(err)
            console.error('Erreur createShare:', err)
        }
        finally {
            this.loading = false
        }
    }
  }
})

function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]!)
  }
  return btoa(binary)
}
