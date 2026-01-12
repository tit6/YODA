<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ShowCreateModal from './components/showCreateModal.vue'
import ShowLinkModal from './components/showLinkModal.vue'
import { useAuthStore } from '@/stores/auth'

interface SharedDocument {
  id: string
  documentName: string
  recipient: string
  createdAt: string
  expiresAt: string
  accessType: 'read' | 'download'
  hasPassword: boolean
  link: string
  accessCount: number
  maxAccess?: number
  status: 'active' | 'expired' | 'revoked'
}

interface SharedDocumentApi {
  object_name: string
  file_name: string
  size: number
  last_modified: string
  dek_encrypted?: string
  iv?: string
  sha256?: string
}

const searchQuery = ref('')
const showCreateModalVisible = ref(false)
const showLinkModalVisible = ref(false)
const generatedLink = ref('')
const generatedLinkHasPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Données de démonstration
const sharedDocuments = ref<SharedDocument[]>([
])

const createShare = (formData: {
  documentName: string
  recipient: string
  duration: string
  accessType: 'read' | 'download'
  requirePassword: boolean
  password: string
  maxAccess: number | null
  token: string
}) => {
  // Génération du lien de partage
  generatedLink.value = `https://localhost:5173/s/${formData.token}`
  generatedLinkHasPassword.value = formData.requirePassword

  // Ajout du nouveau partage
  const expiresAt = new Date()
  expiresAt.setHours(expiresAt.getHours() + parseInt(formData.duration))

  sharedDocuments.value.unshift({
    id: String(Date.now()),
    documentName: formData.documentName,
    recipient: formData.recipient,
    createdAt: new Date().toLocaleString('fr-FR'),
    expiresAt: expiresAt.toLocaleString('fr-FR'),
    accessType: formData.accessType,
    hasPassword: formData.requirePassword,
    link: generatedLink.value,
    accessCount: 0,
    maxAccess: formData.maxAccess || undefined,
    status: 'active'
  })

  // Fermer modal de création et ouvrir modal de lien
  showCreateModalVisible.value = false
  showLinkModalVisible.value = true
}

const formatDate = (value: string) => {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('fr-FR')
}

const fetchSharedDocuments = async () => {
  loading.value = true
  error.value = ''

  try {
    const authStore = useAuthStore()
    const response = await fetch('/api/share/list', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    if (data.status !== 'success') {
      throw new Error(data.message || 'Erreur inconnue')
    }

    const documents = (data.data?.documents || []) as SharedDocumentApi[]
    sharedDocuments.value = documents.map((doc) => ({
      id: doc.object_name,
      documentName: doc.file_name,
      recipient: '-',
      createdAt: formatDate(doc.last_modified),
      expiresAt: '-',
      accessType: 'download',
      hasPassword: false,
      link: '',
      accessCount: 0,
      maxAccess: undefined,
      status: 'active'
    }))
  } catch (err) {
    error.value = String(err)
    console.error('Erreur fetchSharedDocuments:', err)
  } finally {
    loading.value = false
  }
}

const filteredDocuments = computed(() => {
  if (!searchQuery.value) return sharedDocuments.value

  const query = searchQuery.value.toLowerCase()
  return sharedDocuments.value.filter(doc =>
    doc.documentName.toLowerCase().includes(query) ||
    doc.recipient.toLowerCase().includes(query)
  )
})

const revokeShare = (shareId: string) => {
  const share = sharedDocuments.value.find(s => s.id === shareId)
  if (share && confirm(`Êtes-vous sûr de vouloir révoquer le partage de "${share.documentName}" ?`)) {
    share.status = 'revoked'
  }
}

const deleteShare = (shareId: string) => {
  const share = sharedDocuments.value.find(s => s.id === shareId)
  if (share && confirm(`Êtes-vous sûr de vouloir supprimer définitivement ce partage ?`)) {
    const index = sharedDocuments.value.findIndex(s => s.id === shareId)
    sharedDocuments.value.splice(index, 1)
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return '#00c851'
    case 'expired': return '#ffaa00'
    case 'revoked': return '#ff4444'
    default: return '#999'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return 'Actif'
    case 'expired': return 'Expiré'
    case 'revoked': return 'Révoqué'
    default: return status
  }
}

onMounted(() => {
  fetchSharedDocuments()
})
</script>

<template>
  <div class="shared-documents-view">

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button @click="showCreateModalVisible = true" class="btn-primary">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 8C19.6569 8 21 6.65685 21 5C21 3.34315 19.6569 2 18 2C16.3431 2 15 3.34315 15 5C15 6.65685 16.3431 8 18 8Z" stroke="currentColor" stroke-width="2"/>
            <path d="M6 15C7.65685 15 9 13.6569 9 12C9 10.3431 7.65685 9 6 9C4.34315 9 3 10.3431 3 12C3 13.6569 4.34315 15 6 15Z" stroke="currentColor" stroke-width="2"/>
            <path d="M18 22C19.6569 22 21 20.6569 21 19C21 17.3431 19.6569 16 18 16C16.3431 16 15 17.3431 15 19C15 20.6569 16.3431 22 18 22Z" stroke="currentColor" stroke-width="2"/>
            <path d="M8.59 13.51L15.42 17.49M15.41 6.51L8.59 10.49" stroke="currentColor" stroke-width="2"/>
          </svg>
          Créer un partage
        </button>

        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un partage..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- Liste des partages -->
    <div class="shares-section">
      <div class="table-container">
        <table class="shares-table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Destinataire</th>
              <th>Créé le</th>
              <th>Expire le</th>
              <th>Accès</th>
              <th>Sécurité</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="share in filteredDocuments" :key="share.id">
              <td>
                <div class="document-cell">
                  <svg class="file-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V9L13 2ZM18 20H6V4H12V10H18V20Z" fill="currentColor"/>
                  </svg>
                  <span class="document-name">{{ share.documentName }}</span>
                </div>
              </td>
              <td>
                <div class="recipient-cell">
                  <svg class="user-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12Z" fill="currentColor"/>
                    <path d="M12 14C8.13 14 5 15.57 5 17.5V20H19V17.5C19 15.57 15.87 14 12 14Z" fill="currentColor"/>
                  </svg>
                  {{ share.recipient }}
                </div>
              </td>
              <td class="date-cell">{{ share.createdAt }}</td>
              <td class="date-cell">{{ share.expiresAt }}</td>
              <td>
                <div class="access-cell">
                  <span class="access-badge" :class="share.accessType">
                    {{ share.accessType === 'read' ? 'Lecture seule' : 'Téléchargement' }}
                  </span>
                </div>
              </td>
              <td>
                <div class="security-cell">
                  <svg v-if="share.hasPassword" class="lock-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 8H17V6C17 3.24 14.76 1 12 1C9.24 1 7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM12 17C10.9 17 10 16.1 10 15C10 13.9 10.9 13 12 13C13.1 13 14 13.9 14 15C14 16.1 13.1 17 12 17ZM15.1 8H8.9V6C8.9 4.29 10.29 2.9 12 2.9C13.71 2.9 15.1 4.29 15.1 6V8Z" fill="currentColor"/>
                  </svg>
                  <span>{{ share.hasPassword ? 'Protégé' : 'Public' }}</span>
                </div>
              </td>
              <td>
                <span class="status-badge" :style="{ backgroundColor: getStatusColor(share.status) + '20', color: getStatusColor(share.status) }">
                  {{ getStatusText(share.status) }}
                </span>
              </td>
              <td>
                <div class="actions-cell">
                  <button @click="generatedLink = share.link; showLinkModalVisible = true; generatedLinkHasPassword = share.hasPassword" class="action-btn" title="Copier le lien">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button v-if="share.status === 'active'" @click="revokeShare(share.id)" class="action-btn revoke" title="Révoquer">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM15.59 7L12 10.59L8.41 7L7 8.41L10.59 12L7 15.59L8.41 17L12 13.41L15.59 17L17 15.59L13.41 12L17 8.41L15.59 7Z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button @click="deleteShare(share.id)" class="action-btn delete" title="Supprimer">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M16 9V19H8V9H16ZM14.5 3H9.5L8.5 4H5V6H19V4H15.5L14.5 3ZM18 7H6V19C6 20.1 6.9 21 8 21H16C17.1 21 18 20.1 18 19V7Z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Quand ya rien on affiche ça -->
      <div v-if="filteredDocuments.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <path d="M18 8C19.6569 8 21 6.65685 21 5C21 3.34315 19.6569 2 18 2C16.3431 2 15 3.34315 15 5C15 6.65685 16.3431 8 18 8Z" stroke="currentColor" stroke-width="2"/>
          <path d="M6 15C7.65685 15 9 13.6569 9 12C9 10.3431 7.65685 9 6 9C4.34315 9 3 10.3431 3 12C3 13.6569 4.34315 15 6 15Z" stroke="currentColor" stroke-width="2"/>
          <path d="M18 22C19.6569 22 21 20.6569 21 19C21 17.3431 19.6569 16 18 16C16.3431 16 15 17.3431 15 19C15 20.6569 16.3431 22 18 22Z" stroke="currentColor" stroke-width="2"/>
        </svg>
        <h3>Aucun partage trouvé</h3>
        <p>Créez votre premier partage pour commencer</p>
      </div>
    </div>

    <!-- Modals -->
    <ShowCreateModal
      :show="showCreateModalVisible"
      @close="showCreateModalVisible = false"
      @create="createShare"
    />

    <ShowLinkModal
      :show="showLinkModalVisible"
      :link="generatedLink"
      :has-password="generatedLinkHasPassword"
      @close="showLinkModalVisible = false"
    />
  </div>
</template>

<style scoped>
.shared-documents-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-primary:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--primary-active-color);
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* Shares Section */
.shares-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.shares-table {
  width: 100%;
  border-collapse: collapse;
}

.shares-table thead {
  background-color: #f8f9fa;
}

.shares-table th {
  padding: 16px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-active-color);
  border-bottom: 2px solid var(--border-input-color);
  white-space: nowrap;
}

.shares-table td {
  padding: 16px 12px;
  font-size: 14px;
  color: var(--primary-color);
  border-bottom: 1px solid #f0f0f0;
}

.shares-table tbody tr:hover {
  background-color: #f8f9fa;
}

.document-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  width: 24px;
  height: 24px;
  color: var(--primary-active-color);
  flex-shrink: 0;
}

.document-name {
  font-weight: 500;
  color: var(--primary-color);
}

.recipient-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-icon {
  width: 18px;
  height: 18px;
  color: var(--primary-active-color);
  flex-shrink: 0;
}

.date-cell {
  color: var(--primary-active-color);
  font-size: 13px;
  white-space: nowrap;
}

.access-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.access-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.security-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.lock-icon {
  width: 16px;
  height: 16px;
  color: #2e7d32;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--primary-active-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn:hover {
  background-color: #f0f0f0;
  color: var(--primary-color);
}

.action-btn.revoke:hover {
  background-color: #fff3e0;
  color: #ffaa00;
}

.action-btn.delete:hover {
  background-color: #ffebee;
  color: #ff4444;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: var(--primary-active-color);
  opacity: 0.3;
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  color: var(--primary-active-color);
}

/* Responsive */
@media (max-width: 768px) {
  .shares-table {
    font-size: 12px;
  }

  .shares-table th,
  .shares-table td {
    padding: 12px 8px;
  }
}
</style>
