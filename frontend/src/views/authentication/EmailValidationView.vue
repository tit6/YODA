<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const isValidating = ref(false)
const isValidated = ref(false)
const hasError = ref(false)
const userEmail = ref('')

onMounted(async () => {
  // Recuperer l'email depuis le state du router
  const emailFromState = history.state.email as string
  if (emailFromState) {
    userEmail.value = emailFromState
  }
})

const resendEmail = async () => {
  // TODO: Appel API pour renvoyer l'email de validation
  console.log('Resending validation email...')
}
</script>

<template>
  <div class="status-wrapper">
          <div v-if="!isValidating && !isValidated && !hasError" class="status-card">
            <div class="icon-wrapper waiting">
              <svg class="icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" fill="currentColor"/>
              </svg>
            </div>
            <h1 class="title">Vérifiez votre email</h1>
            <p class="description">
              Un email de validation a été envoyé à <strong>{{ userEmail }}</strong>
            </p>
            <p class="description">
              Cliquez sur le lien dans l'email pour activer votre compte.
            </p>

            <div class="actions">
              <button @click="resendEmail" class="resend-btn">
                Renvoyer l'email
              </button>
            </div>
          </div>
        </div>
</template>

<style scoped>
.status-wrapper {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 60px 40px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.icon-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  background-color: var(--blue-warning);
  color: #1976d2;
}

.icon {
  width: 60px;
  height: 60px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-color);
}

.description {
  font-size: 16px;
  color: var(--primary-active-color);
  line-height: 1.6;
  max-width: 400px;
}

.description strong {
  color: var(--primary-color);
  font-weight: 600;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 400px;
  margin-top: 16px;
}

.resend-btn {
  padding: 14px 32px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.resend-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.info-text strong {
  color: var(--primary-color);
}

</style>
