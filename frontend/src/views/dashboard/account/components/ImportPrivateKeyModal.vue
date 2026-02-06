<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  show: boolean
  error: string
  isImporting: boolean
}>()

const emit = defineEmits<{
  close: []
  import: [file: File, passphrase: string]
}>()

const importPassphrase = ref('')
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

function handleClose() {
  importPassphrase.value = ''
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  emit('close')
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

function handleImport() {
  if (selectedFile.value) {
    emit('import', selectedFile.value, importPassphrase.value)
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <h3>Restaurer votre clé privée</h3>

      <div class="warning-box">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div>
          <p><strong>Attention:</strong></p>
          <p>Cette opération va <strong>remplacer votre clé privée actuelle</strong> par celle du fichier de sauvegarde. Assurez-vous d'avoir la bonne passphrase.</p>
        </div>
      </div>

      <div class="input-group">
        <label for="import-file">Fichier de sauvegarde (.json)</label>
        <input
          id="import-file"
          ref="fileInputRef"
          type="file"
          accept=".json,application/json"
          @change="handleFileSelect"
          :disabled="isImporting"
        />
        <p v-if="selectedFile" class="file-name">{{ selectedFile.name }}</p>
      </div>

      <div class="input-group">
        <label for="import-passphrase">Passphrase de déchiffrement</label>
        <input
          id="import-passphrase"
          v-model="importPassphrase"
          type="password"
          placeholder="Saisissez la passphrase utilisée lors de l'export"
          :disabled="isImporting"
        />
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <div class="modal-actions">
        <button class="cancel-btn" @click="handleClose" :disabled="isImporting">Annuler</button>
        <button 
          class="confirm-btn" 
          @click="handleImport" 
          :disabled="isImporting || !selectedFile || !importPassphrase"
        >
          <span v-if="!isImporting">Importer</span>
          <span v-else>Import en cours...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.warning-box {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: #fff3cd;
  border: 2px solid #ffc107;
  border-radius: 8px;
  color: #856404;
}

.warning-box svg {
  flex-shrink: 0;
  stroke: #ffc107;
}

.warning-box p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #856404;
}

.warning-box strong {
  color: #664d03;
}

.file-name {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-muted);
  font-style: italic;
}

input[type="file"] {
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
}

input[type="file"]:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  padding: 12px;
  background-color: #f8d7da;
  border: 1px solid #f5c2c7;
  border-radius: 4px;
}
</style>
