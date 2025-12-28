<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  success: [qrcode: string, secret: string]
}>()

const authStore = useAuthStore()
const password = ref('')
const isLoading = ref(false)
const error = ref('')

function handleClose() {
  password.value = ''
  error.value = ''
  emit('close')
}

async function handleConfirm() {
  if (!password.value) {
    error.value = 'Veuillez saisir votre mot de passe'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/active_a2f', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ password: password.value }),
      credentials: 'include'
    })

    const data = await response.json()

    if (response.ok && data.status === 'success') {
      password.value = ''
      emit('success', data.qrcode, data.secret || '')
    } else {
      error.value = 'Mot de passe incorrect'
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
      <h3>Vérification du mot de passe</h3>
      <div class="input-group">
        <label for="password-verif-a2f">Entrez votre mot de passe pour activer l'authentification à double facteur</label>
      <input
          id="password-verif-a2f"
        type="password"
        v-model="password"
        placeholder="Mot de passe"
        :disabled="isLoading"
        @keyup.enter="handleConfirm"
      />
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
      <div class="modal-actions">
        <button class="cancel-btn" @click="handleClose" :disabled="isLoading">Annuler</button>
        <button class="confirm-btn" @click="handleConfirm" :disabled="isLoading">
          {{ isLoading ? 'Vérification...' : 'Confirmer' }}
        </button>
      </div>
    </div>
  </div>
</template>
