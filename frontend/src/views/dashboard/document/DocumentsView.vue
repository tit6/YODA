<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDocumentsStore } from '@/stores/documents'
import { DEK, PrivateKey } from '@/stores/crypto'
import { decryptFileInChunks } from '@/utils/fileEncryption'
import UploadDocumentModal from '@/views/dashboard/document/components/UploadDocumentModal.vue'
import IconSearch from '@/views/assets/icons/IconSearch.vue'
import IconPlus from '@/views/assets/icons/IconPlus.vue'
import IconDownload from '@/views/assets/icons/IconDownload.vue'
import IconDelete from '@/views/assets/icons/IconDelete.vue'

const documentsStore = useDocumentsStore()
const searchQuery = ref('')
const viewMode = ref('list')
const showUploadModal = ref(false)

onMounted(async () => {
  await documentsStore.fetchDocuments()
})

const filteredDocuments = computed(() => {
  if (!searchQuery.value) {
    return documentsStore.documents
  }
  const query = searchQuery.value.toLowerCase()
  return documentsStore.documents.filter(doc =>
    doc.file_name.toLowerCase().includes(query)
  )
})

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function handleDownload(doc: any) {
  try {

    const result = await documentsStore.downloadDocument(doc.object_name)
    if (!result) {
      return
    }

    // Déchiffrer la DEK avec la clé privée
    const privateKeyJWK = await PrivateKey.GetPrivateKey()
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
      iv,
      doc.size
    )

    // Télécharger le fichier déchiffré
    const url = URL.createObjectURL(decryptedBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = result.fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

  } catch (e) {
    console.error('Erreur lors du téléchargement:', e)
    alert('Erreur lors du téléchargement du fichier')
  }
}

async function handleDelete(doc: any) {
  if (!confirm(`Êtes-vous sûr de vouloir supprimer "${doc.file_name}" ?`)) {
    return
  }

  const success = await documentsStore.deleteDocument(doc.object_name)
  if (success) {
    alert('Document supprimé avec succès')
  } else {
    alert('Erreur lors de la suppression')
  }
}

function handleUploadSuccess() {
  // Rafraîchir la liste des documents
  documentsStore.fetchDocuments()
}
</script>

<template>
  <div class="documents-view">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button @click="showUploadModal = true" class="btn-primary">
          <IconPlus />
          Déposer un document
        </button>

        <div class="search-box">
          <IconSearch class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un document..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- Folders Section -->
    <div class="folders-section">
      <h3 class="section-title">Mes dossiers</h3>
      <div class="folders-grid">
      </div>
    </div>

    <!-- Documents Section -->
    <div class="documents-section">
      <h3 class="section-title">Mes documents</h3>

      <!-- List View -->
      <div v-if="viewMode === 'list' && filteredDocuments.length > 0" class="documents-list">
        <div class="table-container">
          <table class="documents-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Taille</th>
                <th>Date d'upload</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in filteredDocuments" :key="doc.object_name">
                <td>
                  <div class="document-name">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M13 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V9L13 2ZM18 20H6V4H12V10H18V20Z" fill="currentColor"/>
                    </svg>
                    {{ doc.file_name }}
                  </div>
                </td>
                <td>{{ formatFileSize(doc.size) }}</td>
                <td>{{ formatDate(doc.last_modified) }}</td>
                <td>
                  <span class="status-badge encrypted">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L4 5V11C4 16.55 7.84 21.74 13 23C18.16 21.74 22 16.55 22 11V5L14 2H12ZM12 11C13.1 11 14 11.9 14 13C14 14.1 13.1 15 12 15C10.9 15 10 14.1 10 13C10 11.9 10.9 11 12 11Z" fill="currentColor"/>
                    </svg>
                    Chiffré
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn download" @click="handleDownload(doc)" title="Télécharger">
                      <IconDownload />
                    </button>
                    <button class="action-btn delete" @click="handleDelete(doc)" title="Supprimer">
                      <IconDelete />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- aucun document -->
      <div v-if="filteredDocuments.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <path d="M13 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V9L13 2ZM18 20H6V4H12V10H18V20Z" fill="currentColor"/>
          <path d="M8 15.01L8.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 15.01L12.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16 15.01L16.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3>{{ searchQuery ? 'Aucun document trouvé.' : 'Vous n\'avez pas encore de document.' }}</h3>
      </div>

    </div>

    <!-- Modal d'upload -->
    <UploadDocumentModal
      :show="showUploadModal"
      @close="showUploadModal = false"
      @success="handleUploadSuccess"
    />
  </div>
</template>

<style scoped>
.documents-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-lg);
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: var(--space-lg);
  align-items: center;
  flex: 1;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.btn-primary:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-primary svg {
  width: 18px;
  height: 18px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: var(--space-md);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding: 10px var(--space-md) 10px 40px;
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  transition: all var(--transition-base);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.view-btn svg {
  width: 20px;
  height: 20px;
}

/* Folders Section */
.folders-section {
  background: var(--bg-card);
  padding: var(--space-xl);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-lg);
}

.folders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-lg);
}

/* Documents Section */
.documents-section {
  background: var(--bg-card);
  padding: var(--space-xl);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

/* Table View */
.table-container {
  overflow-x: auto;
}

.documents-table {
  width: 100%;
  border-collapse: collapse;
}

.documents-table thead {
  background-color: var(--bg-input-disabled);
}

.documents-table th {
  padding: var(--space-md);
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-muted);
  border-bottom: var(--border-width) solid var(--border-color);
}

.documents-table td {
  padding: var(--space-lg) var(--space-md);
  font-size: var(--font-size-base);
  color: var(--text-primary);
  border-bottom: 1px solid var(--bg-hover);
}

.documents-table tbody tr:hover {
  background-color: var(--bg-input-disabled);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: var(--space-xl);
}

.empty-state h3 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.empty-state p {
  font-size: var(--font-size-base);
  color: var(--text-muted);
  margin-bottom: var(--space-xl);
}

.document-name {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.document-name svg {
  color: var(--text-muted);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.status-badge.encrypted {
  background-color: #d4edda;
  color: #155724;
}

.action-buttons {
  display: flex;
  gap: var(--space-sm);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-sm);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  background-color: transparent;
}

.action-btn:hover {
  background-color: var(--bg-hover);
}

.action-btn.download {
  color: var(--text-primary);
}

.action-btn.download:hover {
  background-color: #e3f2fd;
  color: var(--text-secondary);
}

.action-btn.delete {
  color: var(--color-danger-dark);
}

.action-btn.delete:hover {
  background-color: #f8d7da;
}
</style>
