<script setup lang="ts">
import { ref } from 'vue'
import { DEK, PrivateKey } from '@/stores/crypto'
import { useDocumentsStore } from '@/stores/documents'
import { calculateSHA256InChunks, encryptFileInChunks, blobToBase64InChunks} from '@/utils/fileEncryption'

const props = defineProps<{
  show: boolean
  folderId?: number | null
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const documentsStore = useDocumentsStore()

const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const error = ref('')

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    error.value = ''
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    selectedFile.value = event.dataTransfer.files[0]
    error.value = ''
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
}

function handleClose() {
  if (!isUploading.value) {
    selectedFile.value = null
    error.value = ''
    uploadStatus.value = ''
    uploadProgress.value = 0
    emit('close')
  }
}

async function handleUpload() {
  if (!selectedFile.value) {
    error.value = 'Veuillez sélectionner un fichier'
    return
  }

  isUploading.value = true
  error.value = ''
  uploadProgress.value = 0

  try {
    // Étape 1: Calcul SHA-256 par chunks
    uploadStatus.value = 'Analyse du fichier...'
    uploadProgress.value = 5
    const sha256Hash = await calculateSHA256InChunks(selectedFile.value)
    const sha256 = arrayBufferToBase64(sha256Hash)
    uploadProgress.value = 10

    // Étape 2: Générer DEK et IV
    uploadStatus.value = 'Préparation du chiffrement...'
    const dek = await DEK.GenerateDek()
    const iv = crypto.getRandomValues(new Uint8Array(12))
    uploadProgress.value = 15

    // Étape 3: Chiffrement par chunks
    uploadStatus.value = 'Chiffrement du fichier...'
    const encryptedBlob = await encryptFileInChunks(
      selectedFile.value,
      dek,
      iv,
      (progress) => {
        uploadProgress.value = 15 + Math.floor(progress * 0.45) // 15-60%
      }
    )
    uploadProgress.value = 60

    // Étape 4: Récupérer et chiffrer la DEK
    uploadStatus.value = 'Sécurisation des clés...'
    const token = localStorage.getItem('auth_token')
    const response = await fetch('/api/user/public-key', {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!response.ok) {
      throw new Error('Impossible de récupérer la clé publique')
    }

    const data = await response.json()
    const publicKeyPem = data.data.public_key

    // Importer la clé publique
    const pemContents = publicKeyPem
      .replace(/-----BEGIN PUBLIC KEY-----/, '')
      .replace(/-----END PUBLIC KEY-----/, '')
      .replace(/\s/g, '')
    const binaryDer = Uint8Array.from(atob(pemContents), c => c.charCodeAt(0))
    const publicKey = await crypto.subtle.importKey(
      "spki",
      binaryDer.buffer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      false,
      ["encrypt"]
    )

    // Chiffrer la DEK
    const dekRaw = await crypto.subtle.exportKey("raw", dek)
    const dekEncryptedBuffer = await crypto.subtle.encrypt(
      { name: "RSA-OAEP" },
      publicKey,
      dekRaw
    )
    const dekEncrypted = arrayBufferToBase64(dekEncryptedBuffer)
    uploadProgress.value = 70

    // Étape 5: Conversion en base64 par chunks
    uploadStatus.value = 'Préparation de l\'upload...'
    const fileDataB64 = await blobToBase64InChunks(encryptedBlob)
    uploadProgress.value = 80

    // Étape 6: Upload vers le serveur
    uploadStatus.value = 'Upload en cours...'
    const success = await documentsStore.uploadDocument({
      file_name: selectedFile.value.name,
      file_data: fileDataB64,
      dek_encrypted: dekEncrypted,
      iv: arrayBufferToBase64(iv),
      sha256: sha256,
      folder_id: props.folderId ?? null
    })

    if (success) {
      uploadProgress.value = 100
      uploadStatus.value = 'Upload terminé avec succès !'
      emit('success')

      // Fermer le modal après 1 seconde
      setTimeout(() => {
        handleClose()
      }, 1000)
    } else {
      throw new Error(documentsStore.error || 'Erreur lors de l\'upload')
    }

  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Erreur lors de l\'upload'
    uploadStatus.value = ''
    uploadProgress.value = 0
  } finally {
    isUploading.value = false
  }
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]!)
  }
  return btoa(binary)
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content upload-modal" @click.stop>
      <h3>Déposer un document</h3>

      <div
        class="dropzone"
        :class="{ 'has-file': selectedFile }"
        @drop="handleDrop"
        @dragover="handleDragOver"
        @click="() => !isUploading && $refs.fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          style="display: none"
          @change="handleFileSelect"
          :disabled="isUploading"
        />

        <div v-if="!selectedFile" class="dropzone-content">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M17 8L12 3M12 3L7 8M12 3V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p><strong>Cliquez pour sélectionner</strong> ou glissez-déposez un fichier</p>
        </div>

        <div v-else class="file-info">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V9L13 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13 2V9H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p class="file-name">{{ selectedFile.name }}</p>
          <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
        </div>
      </div>

      <div v-if="isUploading" class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p class="progress-status">{{ uploadStatus }}</p>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <div class="modal-actions">
        <button class="cancel-btn" @click="handleClose" :disabled="isUploading">Annuler</button>
        <button
          class="confirm-btn"
          @click="handleUpload"
          :disabled="!selectedFile || isUploading"
        >
          <span v-if="!isUploading">Uploader</span>
          <span v-else>Upload en cours...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dropzone {
  border: 2px dashed var(--border-input-color);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.dropzone:hover {
  border-color: var(--primary-color);
  background-color: #f8f9fa;
}

.dropzone.has-file {
  border-color: var(--primary-color);
  background-color: #f0f8ff;
}

.dropzone-content svg {
  color: var(--primary-active-color);
  margin-bottom: 12px;
}

.dropzone-content p {
  margin: 0;
  font-size: 14px;
  color: var(--primary-color);
}

.file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.file-info svg {
  color: var(--primary-color);
}

.file-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
  word-break: break-word;
}

.file-size {
  font-size: 14px;
  color: var(--primary-active-color);
}

.progress-container {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-status {
  font-size: 14px;
  color: var(--primary-color);
  text-align: center;
  margin: 0;
}
</style>
