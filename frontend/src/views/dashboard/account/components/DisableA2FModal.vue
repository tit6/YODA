<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const authStore = useAuthStore()
const disablePassword = ref('')
const disableOtp = ref('')
const isLoading = ref(false)
const error = ref('')

function handleClose() {
  disablePassword.value = ''
  disableOtp.value = ''
  error.value = ''
  emit('close')
}

async function handleConfirm() {
  if (!disablePassword.value) {
    error.value = 'Veuillez saisir votre mot de passe'
    return
  }

  if (!disableOtp.value || disableOtp.value.length !== 6) {
    error.value = 'Veuillez saisir un code à 6 chiffres'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/disable_a2f', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        password: disablePassword.value,
        otp: disableOtp.value
      }),
      credentials: 'include'
    })

    const data = await response.json()

    if (response.ok && data.status === 'success') {
      disablePassword.value = ''
      disableOtp.value = ''
      emit('success')
      alert('A2F désactivée avec succès')
    } else {
      error.value = 'Mot de passe ou code incorrect'
    }
  } catch (err) {
    console.error('Erreur:', err)
    error.value = 'Erreur de connexion'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <h3>Désactiver l'authentification à double facteur</h3>

      <div class="input-group">
        <label for="disable-password">Mot de passe</label>
        <input
          id="disable-password"
          v-model="disablePassword"
          type="password"
          placeholder="Votre mot de passe"
          :disabled="isLoading"
        />
      </div>

      <div class="input-group">
        <label for="disable-otp">Code de vérification</label>
        <input
          id="disable-otp"
          v-model="disableOtp"
          type="text"
          placeholder="000000"
          maxlength="6"
          class="otp-input"
          :disabled="isLoading"
          @keyup.enter="handleConfirm"
        />
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <div class="modal-actions">
        <button class="cancel-btn" @click="handleClose" :disabled="isLoading">Annuler</button>
        <button class="confirm-btn" @click="handleConfirm" :disabled="isLoading">
          {{ isLoading ? 'Désactivation...' : 'Désactiver l\'A2F' }}
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

.modal-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
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

.otp-input {
  text-align: center;
  letter-spacing: 8px;
  font-family: 'Courier New', monospace;
  font-size: 18px !important;
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
