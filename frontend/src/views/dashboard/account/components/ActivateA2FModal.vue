<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  show: boolean
  qrCodeBase64: string
  secretKey: string
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const authStore = useAuthStore()
const otpcode = ref('')
const isLoading = ref(false)
const error = ref('')

function handleClose() {
  otpcode.value = ''
  error.value = ''
  emit('close')
}

async function handleConfirm() {
  if (!otpcode.value || otpcode.value.length !== 6) {
    error.value = 'Veuillez saisir un code à 6 chiffres'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/check_a2f', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ otp: otpcode.value }),
      credentials: 'include'
    })

    const data = await response.json()

    if (data.status === 'success') {
      otpcode.value = ''
      emit('success')
    } else {
      error.value = 'Code incorrect'
    }
  } catch (err) {
    console.error('Erreur:', err)
    error.value = 'Erreur de connexion'
  } finally {
    isLoading.value = false
  }
}

function copySecretKey() {
  navigator.clipboard.writeText(props.secretKey)
    .then(() => alert('Clé secrète copiée!'))
    .catch(() => alert('Erreur lors de la copie'))
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content modal-a2f" @click.stop>
      <h3>Activer l'authentification à double facteur</h3>
      <p>Scannez ce QR code avec votre application d'authentification (Google Authenticator, Authy, etc.)</p>

      <div class="qr-container">
        <img :src="qrCodeBase64" alt="QR Code" class="qr-code" />
      </div>

      <div class="secret-key">
        <label>Clé secrète (si vous ne pouvez pas scanner) :</label>
        <div class="key-container">
          <code>{{ secretKey }}</code>
          <button class="copy-btn" title="Copier" @click="copySecretKey">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 9H11C9.89543 9 9 9.89543 9 11V20C9 21.1046 9.89543 22 11 22H20C21.1046 22 22 21.1046 22 20V11C22 9.89543 21.1046 9 20 9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5 15H4C3.46957 15 2.96086 14.7893 2.58579 14.4142C2.21071 14.0391 2 13.5304 2 13V4C2 3.46957 2.21071 2.96086 2.58579 2.58579C2.96086 2.21071 3.46957 2 4 2H13C13.5304 2 14.0391 2.21071 14.4142 2.58579C14.7893 2.96086 15 3.46957 15 4V5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="verification-code">
        <label>Entrez le code de vérification :</label>
        <input
          v-model="otpcode"
          type="text"
          placeholder="000000"
          maxlength="6"
          :disabled="isLoading"
          @keyup.enter="handleConfirm"
        />
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <div class="modal-actions">
        <button class="cancel-btn" @click="handleClose" :disabled="isLoading">Annuler</button>
        <button class="confirm-btn" @click="handleConfirm" :disabled="isLoading">
          {{ isLoading ? 'Vérification...' : 'Activer l\'A2F' }}
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

.modal-a2f {
  max-width: 600px;
}

.modal-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.modal-content p {
  font-size: 15px;
  color: var(--primary-hover-color);
  margin: 0;
}

.qr-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.qr-code {
  width: 200px;
  height: 200px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  background-color: white;
  padding: 10px;
}

.secret-key {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.secret-key label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-hover-color);
}

.key-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: #fafafa;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
}

.key-container code {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: var(--primary-color);
  letter-spacing: 2px;
}

.copy-btn {
  padding: 6px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: var(--primary-color);
  border-radius: 4px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-btn:hover {
  background-color: var(--border-input-color);
}

.verification-code {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.verification-code label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-hover-color);
}

.verification-code input {
  padding: 12px 16px;
  border: 2px solid var(--border-input-color);
  border-radius: 8px;
  font-size: 18px;
  text-align: center;
  letter-spacing: 8px;
  font-family: 'Courier New', monospace;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.verification-code input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
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

.cancel-btn:hover {
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

.error-message {
  color: var(--red-warning);
  font-size: 14px;
  margin: 0;
}
</style>
