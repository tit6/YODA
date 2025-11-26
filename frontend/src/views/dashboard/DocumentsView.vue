<script setup lang="ts">
import { ref } from 'vue'

interface Document {
  id: number
  name: string
  size: string
  type: string
  encrypted: boolean
  shared: boolean
  uploadDate: string
  lastAccess: string
  folder: string
}

const searchQuery = ref('')
const viewMode = ref('list')
const showUploadModal = ref(false)
</script>

<template>
  <div class="documents-view">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button @click="showUploadModal = true" class="btn-primary">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" fill="currentColor"/>
          </svg>
          Déposer un document
        </button>

        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
          </svg>
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
      <div v-if="viewMode === 'list'" class="documents-list">
        <div class="table-container">
          <table class="documents-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Taille</th>
                <th>Dossier</th>
                <th>Date d'upload</th>
                <th>Dernier accès</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
            </tbody>
          </table>
        </div>
      </div>

      <!-- aucun document -->
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <path d="M13 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V9L13 2ZM18 20H6V4H12V10H18V20Z" fill="currentColor"/>
          <path d="M8 15.01L8.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 15.01L12.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16 15.01L16.01 14.99" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3>Vous n'avez pas encore de document.</h3>
      </div>

    </div>
  </div>
</template>

<style scoped>
.documents-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.view-btn svg {
  width: 20px;
  height: 20px;
}

/* Folders Section */
.folders-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.folders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

/* Documents Section */
.documents-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
  background-color: #f8f9fa;
}

.documents-table th {
  padding: 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-active-color);
  border-bottom: 2px solid var(--border-input-color);
}

.documents-table td {
  padding: 16px 12px;
  font-size: 14px;
  color: var(--primary-color);
  border-bottom: 1px solid #f0f0f0;
}

.documents-table tbody tr:hover {
  background-color: #f8f9fa;
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
  color: var(--primary-active-color);
  opacity: 0.5;
  margin-bottom: 20px;
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
  margin-bottom: 24px;
}
</style>
