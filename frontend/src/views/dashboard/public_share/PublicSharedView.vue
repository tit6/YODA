<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { PrivateKeyExport } from '@/stores/crypto'
import { decryptFileInChunks } from '@/utils/fileEncryption'

const route = useRoute()

const token = computed(() => {
  const rawToken = route.params.token
  if (!rawToken) return ''
  return Array.isArray(rawToken) ? rawToken.join('/') : String(rawToken)
})

const email = ref('')
const password = ref('')
const fileName = ref('')
const loading = ref(false)
const error = ref('')
const downloading = ref(false)
const downloadError = ref('')

const canSubmit = computed(() => {
  return Boolean(email.value.trim()) && password.value.length > 0
})

const placeholderText = computed(() => {
  if (!token.value) return 'Lien de partage invalide.'
  if (loading.value) return 'Chargement du nom du fichier...'
  if (error.value) return 'Impossible de recuperer le nom du fichier.'
  return 'Nom du fichier indisponible.'
})

const fetchFileName = async (tokenValue: string) => {
  error.value = ''
  fileName.value = ''

  if (!tokenValue) {
    error.value = 'Lien de partage invalide.'
    return
  }

  loading.value = true
  try {
    const response = await fetch('/api/share/name_file', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token: tokenValue })
    })

    let data: any = null
    try {
      data = await response.json()
    } catch (parseError) {
      data = null
    }

    if (!response.ok) {
      const message = data?.message || `Erreur ${response.status}`
      throw new Error(message)
    }

    if (!data || data.status !== 'success') {
      const message = data?.message || 'Erreur lors de la recuperation du fichier.'
      throw new Error(message)
    }

    if (!data.file_name) {
      throw new Error('Nom du fichier indisponible.')
    }

    fileName.value = data.file_name
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erreur lors de la recuperation du fichier.'
  } finally {
    loading.value = false
  }
}

const extractFileName = (headers: Headers) => {
  const contentDisposition = headers.get('Content-Disposition') || ''
  const match = /filename\*?=(?:UTF-8''|\"?)([^\";]+)/i.exec(contentDisposition)
  if (match && match[1]) {
    try {
      return decodeURIComponent(match[1])
    } catch (err) {
      return match[1]
    }
  }
  return fileName.value || 'document'
}

const base64ToBytes = (value: string) => {
  return Uint8Array.from(atob(value), (c) => c.charCodeAt(0))
}

const resolveDekKey = async (dekPayload: string, ivBytes: Uint8Array, passphrase: string) => {
  const rawBytes = base64ToBytes(dekPayload)
  if (rawBytes.byteLength === 32) {
    return crypto.subtle.importKey(
      'raw',
      rawBytes,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    )
  }

  if (!passphrase) {
    throw new Error('Mot de passe requis pour dechiffrer.')
  }

  const { kek } = await PrivateKeyExport.deriveKeyFromPassphrase(passphrase, ivBytes)
  const dekRaw = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: ivBytes },
    kek,
    rawBytes
  )

  return crypto.subtle.importKey(
    'raw',
    dekRaw,
    { name: 'AES-GCM', length: 256 },
    false,
    ['decrypt']
  )
}

const handleSubmit = async () => {
  downloadError.value = ''
  if (!canSubmit.value || !token.value) return

  downloading.value = true
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    const authToken = localStorage.getItem('auth_token')
    if (authToken) {
      headers.Authorization = `Bearer ${authToken}`
    }

    const response = await fetch('/api/share/download', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        token: token.value,
        email: email.value.trim(),
        password: password.value
      })
    })

    if (!response.ok) {
      const contentType = response.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        const data = await response.json()
        throw new Error(data?.message || data?.error || `Erreur ${response.status}`)
      }
      throw new Error(`Erreur ${response.status}`)
    }

    const dekEncrypted = response.headers.get('X-DEK-Encrypted') || ''
    const iv = response.headers.get('X-IV') || ''

    if (!dekEncrypted || !iv) {
      throw new Error('Metadonnees de dechiffrement manquantes.')
    }

    const encryptedBlob = await response.blob()
    const ivBytes = base64ToBytes(iv)
    const dek = await resolveDekKey(dekEncrypted, ivBytes, password.value)
    const decryptedBlob = await decryptFileInChunks(encryptedBlob, dek, ivBytes)

    const downloadName = extractFileName(response.headers)
    const url = URL.createObjectURL(decryptedBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = downloadName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (err) {
    downloadError.value = err instanceof Error ? err.message : 'Erreur lors du telechargement.'
  } finally {
    downloading.value = false
  }
}

watch(token, (value) => {
  fetchFileName(value)
}, { immediate: true })
</script>

<template>
  <div class="public-share-page">
    <div class="share-card">
      <div class="file-header">
        <span class="file-label">Nom du fichier</span>
        <span v-if="fileName" class="file-name">{{ fileName }}</span>
        <span v-else class="file-name placeholder">
          <span v-if="loading" class="loading-spinner"></span>
          <span>{{ placeholderText }}</span>
        </span>
      </div>

      <form class="share-form" @submit.prevent="handleSubmit">
        <div class="input-group">
          <label for="share-email">Email</label>
          <input
            id="share-email"
            v-model.trim="email"
            type="email"
            placeholder="vous@exemple.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="input-group">
          <label for="share-password">Mot de passe</label>
          <input
            id="share-password"
            v-model="password"
            type="password"
            placeholder="Mot de passe du partage"
            autocomplete="current-password"
            required
          />
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading || downloading || !canSubmit">
          {{ downloading ? 'Telechargement...' : 'Telecharger' }}
        </button>
      </form>

      <p v-if="downloadError" class="download-error">{{ downloadError }}</p>
    </div>
  </div>
</template>

<style scoped>
.public-share-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: linear-gradient(135deg, #f5f5f5 0%, #efefef 50%, #fdfdfd 100%);
}

.share-card {
  width: 100%;
  max-width: 520px;
  background: var(--bg-card);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.file-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
}

.file-name {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  word-break: break-word;
}

.file-name.placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-weight: var(--font-weight-medium);
}

.share-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-form .btn {
  width: 100%;
}

.download-error {
  margin: 0;
  font-size: 13px;
  color: var(--color-danger-dark);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.15);
  border-top-color: var(--primary-color);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 600px) {
  .share-card {
    padding: 24px;
  }
}
</style>
