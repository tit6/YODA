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
.otp-input {
  text-align: center;
  letter-spacing: 8px;
  font-family: 'Courier New', monospace;
  font-size: 18px !important;
}
</style>
