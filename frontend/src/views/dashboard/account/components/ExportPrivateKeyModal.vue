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
    <div class="modal-content modal-export" @click.stop>
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
.modal-overlay {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background-color: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-export {
  max-width: 550px;
}

.modal-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

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

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-hover-color);
}

.input-group input {
  padding: 12px 16px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
}

.input-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: var(--red-warning);
  font-size: 14px;
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn, .confirm-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: var(--primary-color);
}

.cancel-btn:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.confirm-btn {
  background-color: var(--primary-color);
  color: var(--secondary-color);
}

.confirm-btn:hover:not(:disabled) {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.cancel-btn:disabled,
.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
