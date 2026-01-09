<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  show: boolean
  error: string
  isExporting: boolean
}>()

const emit = defineEmits<{
  close: []
  export: [passphrase: string, confirmPassphrase: string]
}>()

const exportPassphrase = ref('')
const exportConfirmPassphrase = ref('')

function handleClose() {
  exportPassphrase.value = ''
  exportConfirmPassphrase.value = ''
  emit('close')
}

function handleExport() {
  emit('export', exportPassphrase.value, exportConfirmPassphrase.value)
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <h3>Sauvegarder votre clé privée</h3>

      <div class="warning-box">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div>
          <p><strong>Important:</strong></p>
          <p>Votre clé privée sera chiffrée avec une passphrase. <strong>Sans cette passphrase, la restauration sera impossible.</strong> Conservez-la en lieu sûr.</p>
        </div>
      </div>

      <div class="input-group">
        <label for="export-passphrase">Passphrase de protection (min. 12 caractères)</label>
        <input
          id="export-passphrase"
          v-model="exportPassphrase"
          type="password"
          placeholder="Saisissez une passphrase forte"
          :disabled="isExporting"
        />
      </div>

      <div class="input-group">
        <label for="export-confirm-passphrase">Confirmer la passphrase</label>
        <input
          id="export-confirm-passphrase"
          v-model="exportConfirmPassphrase"
          type="password"
          placeholder="Confirmez la passphrase"
          :disabled="isExporting"
        />
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <div class="modal-actions">
        <button class="cancel-btn" @click="handleClose" :disabled="isExporting">Annuler</button>
        <button class="confirm-btn" @click="handleExport" :disabled="isExporting">
          <span v-if="!isExporting">Exporter</span>
          <span v-else>Export en cours...</span>
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
</style>
