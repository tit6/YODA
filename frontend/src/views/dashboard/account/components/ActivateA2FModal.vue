<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import IconCopy from '@/views/assets/icons/IconCopy.vue'

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
            <IconCopy />
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
.modal-a2f {
  max-width: 600px;
}

.qr-container {
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
  background-color: var(--bg-input);
  border-radius: var(--border-radius-md);
}

.qr-code {
  width: 200px;
  height: 200px;
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-card);
  padding: var(--space-sm);
}

.secret-key {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.secret-key label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
}

.key-container {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background-color: var(--bg-input);
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-md);
}

.key-container code {
  flex: 1;
  font-family: var(--font-mono);
  font-size: var(--font-size-base);
  color: var(--text-primary);
  letter-spacing: 2px;
}

.copy-btn {
  padding: var(--space-sm);
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-primary);
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-btn svg {
  width: 16px;
  height: 16px;
}

.copy-btn:hover {
  background-color: var(--border-color);
}

.verification-code {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.verification-code label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
}

.verification-code input {
  padding: var(--space-md) var(--space-lg);
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-xl);
  text-align: center;
  letter-spacing: 8px;
  font-family: var(--font-mono);
  transition: all var(--transition-base);
  background-color: var(--bg-input);
}

.verification-code input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
}
</style>
