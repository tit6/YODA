<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const verificationCode = ref('')
const useRecoveryCode = ref(false)
const error = ref('')
const isLoading = ref(false)

const verify2FA = async () => {
  error.value = ''
  isLoading.value = true

  if (!useRecoveryCode.value && verificationCode.value.length !== 6) {
    error.value = 'Le code doit contenir 6 chiffres'
    isLoading.value = false
    return
  }

  if (useRecoveryCode.value && verificationCode.value.length < 8) {
    error.value = 'Code de récupération invalide'
    isLoading.value = false
    return
  }

  try {
    const response = await fetch('/api/a2f_login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({otp: verificationCode.value}),
      credentials: 'include'
    })

    const data = await response.json()

    if (data.status === 'success' && data.token) {
      // Remplacer l'ancien token par le nouveau
      localStorage.setItem('auth_token', data.token)
      authStore.token = data.token
      authStore.requires_a2f = false
      authStore.isAuthenticated = true

      await router.push({name: 'dashboard-documents' })
    } else {
      error.value = 'code invalide'
    }

  } finally {
    isLoading.value = false
  }
}

const toggleRecoveryMode = () => {
  useRecoveryCode.value = !useRecoveryCode.value
  verificationCode.value = ''
  error.value = ''
}
</script>

<template>
<div class="form-wrapper">
          <div class="icon-wrapper">
            <svg class="icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1ZM12 11.99H19C18.47 16.11 15.72 19.78 12 20.93V12H5V6.3L12 3.19V11.99Z" fill="currentColor"/>
            </svg>
          </div>

          <h1 class="title">Authentification a2f</h1>

          <form @submit.prevent="verify2FA" class="verification-form">
            <div class="input-group">
              <input
                v-model="verificationCode"
                type="text"
                :maxlength="useRecoveryCode ? 16 : 6"
                :pattern="useRecoveryCode ? '[A-Za-z0-9-]+' : '[0-9]{6}'"
                :placeholder="useRecoveryCode ? 'XXXX-XXXX-XXXX' : '123456'"
                class="verification-input"
                :class="{ error: error, recovery: useRecoveryCode }"
                @input="error = ''"
                autofocus
              />
            </div>

            <p v-if="error" class="error-message">{{ error }}</p>

            <button
              type="submit"
              class="verify-btn"
              :disabled="isLoading || verificationCode.length < 6"
            >
              <span v-if="!isLoading">Vérifier</span>
              <span v-else class="loading-text">
                <span class="spinner-small"></span>
                Vérification...
              </span>
            </button>
          </form>

          <div class="divider">
            <span>ou</span>
          </div>

          <button @click="toggleRecoveryMode" class="toggle-btn">
            {{ useRecoveryCode
              ? 'Utiliser l\'application d\'authentification'
              : 'Utiliser un code de récupération'
            }}
          </button>
        </div>
</template>

<style scoped>
.form-wrapper {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 60px 40px;
  flex: 1;
  align-items: center;
  justify-content: center;
}

.icon-wrapper {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  border-radius: 50%;
  background-color: #e8f5e9;
  color: #388e3c;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  width: 50px;
  height: 50px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
  margin-left: 15%;
}

.verification-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.input-group {
  display: flex;
  justify-content: center;
}

.verification-input {
  width: 100%;
  max-width: 350px;
  padding: 20px;
  font-size: 32px;
  font-weight: 700;
  text-align: center;
  letter-spacing: 12px;
  border: 2px solid #e5e5e5;
  border-radius: 8px;
  background-color: #fafafa;
  transition: all 0.3s ease;
}

.verification-input.recovery {
  font-size: 20px;
  letter-spacing: 2px;
}

.verification-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: #ffffff;
}

.verification-input.error {
  border-color: #FF5465;
  background-color: #fff5f5;
}

.error-message {
  color: #FF5465;
  font-size: 14px;
  text-align: center;
  margin-top: -8px;
}

.verify-btn {
  padding: 16px 32px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.verify-btn:hover:not(:disabled) {
  background-color: var(--primary-hover-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.verify-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #999;
  font-size: 14px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background-color: #e5e5e5;
}

.divider span {
  padding: 0 16px;
}

.toggle-btn {
  padding: 12px 24px;
  background-color: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.toggle-btn:hover {
  background-color: var(--primary-color);
  color: var(--secondary-color);
}

.help-text p {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.help-text strong {
  color: var(--primary-color);
  font-size: 14px;
  display: block;
  margin-bottom: 8px;
}
</style>
