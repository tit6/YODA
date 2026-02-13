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
const showNewFolderInput = ref(false)
const newFolderName = ref('')

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

const filteredFolders = computed(() => {
  if (!searchQuery.value) {
    return documentsStore.folders
  }
  const query = searchQuery.value.toLowerCase()
  return documentsStore.folders.filter(folder =>
    folder.name.toLowerCase().includes(query)
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

function navigateToFolder(folderId: number | null) {
  searchQuery.value = ''
  documentsStore.navigateToFolder(folderId)
}

async function handleCreateFolder() {
  const name = newFolderName.value.trim()
  if (!name) return

  const success = await documentsStore.createFolder(name, documentsStore.currentFolderId)
  if (success) {
    newFolderName.value = ''
    showNewFolderInput.value = false
  } else {
    alert('Erreur lors de la création du dossier')
  }
}

function cancelCreateFolder() {
  newFolderName.value = ''
  showNewFolderInput.value = false
}

async function handleDeleteFolder(folder: any) {
  if (!confirm(`Êtes-vous sûr de vouloir supprimer le dossier "${folder.name}" et tout son contenu ?`)) {
    return
  }

  const success = await documentsStore.deleteFolder(folder.id)
  if (success) {
    alert('Dossier supprimé avec succès')
  } else {
    alert('Erreur lors de la suppression du dossier')
  }
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
  documentsStore.fetchDocuments(documentsStore.currentFolderId)
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

        <button @click="showNewFolderInput = true" class="btn-secondary" v-if="!showNewFolderInput">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6H12L10 4Z" fill="currentColor"/>
            <path d="M12 10V16M9 13H15" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
          Nouveau dossier
        </button>

        <div class="search-box">
          <IconSearch class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- Breadcrumb -->
    <div class="breadcrumb" v-if="documentsStore.breadcrumb.length > 0 || documentsStore.currentFolderId !== null">
      <span class="breadcrumb-item clickable" @click="navigateToFolder(null)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 12L5 10M5 10L12 3L19 10L21 12M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9.55228 21 10 20.5523 10 20V16C10 15.4477 10.4477 15 11 15H13C13.5523 15 14 15.4477 14 16V20C14 20.5523 14.4477 21 15 21M9 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Mes fichiers
      </span>
      <template v-for="(crumb, index) in documentsStore.breadcrumb" :key="crumb.id">
        <span class="breadcrumb-separator">/</span>
        <span
          class="breadcrumb-item"
          :class="{ clickable: index < documentsStore.breadcrumb.length - 1 }"
          @click="index < documentsStore.breadcrumb.length - 1 ? navigateToFolder(crumb.id) : null"
        >
          {{ crumb.name }}
        </span>
      </template>
    </div>

    <!-- New Folder Input -->
    <div v-if="showNewFolderInput" class="new-folder-bar">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="folder-icon-input">
        <path d="M10 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6H12L10 4Z" fill="currentColor"/>
      </svg>
      <input
        v-model="newFolderName"
        type="text"
        placeholder="Nom du dossier..."
        class="new-folder-input"
        @keyup.enter="handleCreateFolder"
        @keyup.escape="cancelCreateFolder"
        autofocus
      />
      <button class="btn-confirm-folder" @click="handleCreateFolder" :disabled="!newFolderName.trim()">
        Créer
      </button>
      <button class="btn-cancel-folder" @click="cancelCreateFolder">
        Annuler
      </button>
    </div>

    <!-- Folders Section -->
    <div class="folders-section" v-if="filteredFolders.length > 0">
      <h3 class="section-title">Dossiers</h3>
      <div class="folders-grid">
        <div
          v-for="folder in filteredFolders"
          :key="folder.id"
          class="folder-card"
          @click="navigateToFolder(folder.id)"
        >
          <div class="folder-card-content">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="folder-icon">
              <path d="M10 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6H12L10 4Z" fill="currentColor"/>
            </svg>
            <span class="folder-name">{{ folder.name }}</span>
          </div>
          <button
            class="folder-delete-btn"
            @click.stop="handleDeleteFolder(folder)"
            title="Supprimer le dossier"
          >
            <IconDelete />
          </button>
        </div>
      </div>
    </div>

    <!-- Documents Section with transition -->
    <Transition name="docs-fade" mode="out-in">
    <div class="documents-section" :key="documentsStore.currentFolderId ?? 'root'">
      <h3 class="section-title">Documents</h3>

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
      <div v-if="filteredDocuments.length === 0 && filteredFolders.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <path d="M13 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V9L13 2ZM18 20H6V4H12V10H18V20Z" fill="currentColor"/>
          <path d="M8 15.01L8.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 15.01L12.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16 15.01L16.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3>{{ searchQuery ? 'Aucun résultat trouvé.' : 'Ce dossier est vide.' }}</h3>
        <p v-if="!searchQuery">Déposez un document ou créez un nouveau dossier pour commencer.</p>
      </div>

    </div>
    </Transition>

    <!-- Modal d'upload -->
    <UploadDocumentModal
      :show="showUploadModal"
      :folder-id="documentsStore.currentFolderId"
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

/* Documents transition on folder change */
.docs-fade-enter-active,
.docs-fade-leave-active {
  transition: opacity 0.2s ease;
}

.docs-fade-enter-from,
.docs-fade-leave-to {
  opacity: 0;
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

.btn-secondary {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  background-color: var(--bg-card);
  color: var(--text-primary);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.btn-secondary svg {
  width: 18px;
  height: 18px;
  color: var(--primary-color);
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

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-card);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  font-size: var(--font-size-base);
  flex-wrap: wrap;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-muted);
  font-weight: var(--font-weight-semibold);
}

.breadcrumb-item.clickable {
  color: var(--primary-color);
  cursor: pointer;
}

.breadcrumb-item.clickable:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: var(--text-muted);
  margin: 0 2px;
}

/* New Folder Input Bar */
.new-folder-bar {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-card);
  border-radius: var(--border-radius-md);
  width: 50%;
  border: var(--border-width) solid var(--border-color);
}

.folder-icon-input {
  color: var(--primary-color);
  flex-shrink: 0;
}

.new-folder-input {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-base);
  outline: none;
}

.new-folder-input:focus {
  border-color: var(--primary-color);
}

.btn-confirm-folder {
  padding: var(--space-sm) var(--space-lg);
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-confirm-folder:hover:not(:disabled) {
  background-color: var(--primary-hover-color);
}

.btn-confirm-folder:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel-folder {
  padding: var(--space-sm) var(--space-lg);
  background-color: transparent;
  color: var(--text-muted);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel-folder:hover {
  background-color: var(--bg-hover);
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

.folder-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg);
  background-color: var(--bg-input-disabled);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  border: var(--border-width) solid transparent;
}

.folder-card:hover {
  background-color: var(--bg-hover);
  border-color: var(--primary-color);
}

.folder-card-content {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  min-width: 0;
}

.folder-icon {
  color: var(--primary-color);
  flex-shrink: 0;
}

.folder-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.folder-delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-md);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  background-color: transparent;
  color: var(--text-muted);
  transition: all var(--transition-fast);
  opacity: 0;
  flex-shrink: 0;
}

.folder-card:hover .folder-delete-btn {
  opacity: 1;
}

.folder-delete-btn:hover {
  background-color: #f8d7da;
  color: var(--color-danger-dark);
}

.folder-delete-btn svg {
  width: 16px;
  height: 16px;
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
