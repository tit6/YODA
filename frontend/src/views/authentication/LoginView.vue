<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isLogin = ref(true)
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const name = ref('')
const firstName = ref('')
const submitted = ref(false)

const passwordStrength = computed(() => {
  if (isLogin.value || !password.value) return 0

  let strength = 0
  const pwd = password.value

  // Minimum 16 caractères
  if (pwd.length >= 16) strength++

  // Une minuscule
  if (/[a-z]/.test(pwd)) strength++

  // Une majuscule
  if (/[A-Z]/.test(pwd)) strength++

  // Un chiffre
  if (/[0-9]/.test(pwd)) strength++

  // Un caractère spécial
  if (/[^a-zA-Z0-9]/.test(pwd)) strength++

  // Retourne un niveau de 0 à 3 (faible, moyen, fort)
  if (strength <= 2) return 1 // Rouge
  if (strength <= 4) return 2 // Jaune
  return 3 // Vert
})

const isPasswordValid = computed(() => {
  if (isLogin.value) return true
  const pwd = password.value
  return pwd.length >= 16 &&
         /[a-z]/.test(pwd) &&
         /[A-Z]/.test(pwd) &&
         /[0-9]/.test(pwd) &&
         /[^a-zA-Z0-9]/.test(pwd)
})

const handleSubmit = async () => {
  submitted.value = true

  if (isLogin.value) {
    await authStore.login({ email: email.value, password: password.value })

    if (!authStore.error) {
      if (authStore.requires_a2f) {
        await router.push({path: '/auth/verify-2fa'})
      } else if (authStore.isAuthenticated) {
        await router.push({path: '/dashboard/documents'})
      }
    }
  } else {
    if (password.value !== confirmPassword.value) {
      const confirmPasswordError = document.getElementById('confirm-password')
      if (confirmPasswordError) {
        confirmPasswordError.style.borderColor = '#FF5465'
      }
      return
    }

    if (!isPasswordValid.value) {
      authStore.error = 'Le mot de passe doit contenir au minimum 16 caractères, 4 chiffres et 1 caractère spécial'
      return
    }

    const success = await authStore.register({
      name: name.value,
      prenom: firstName.value,
      email: email.value,
      password: password.value,
      second_password: confirmPassword.value
    })

    if (success) {
      // Basculer vers l'onglet connexion après l'enregistrement
      isLogin.value = true
      submitted.value = false
    }
  }
}
</script>

<template>
  <!-- Switch tabs -->
  <div class="tabs">
    <button
      :class="['tab', { active: isLogin }]"
      @click="isLogin = true; submitted = false"
    >
      Connexion
    </button>
    <button
      :class="['tab', { active: !isLogin }]"
      @click="isLogin = false; submitted = false"
    >
      Enregistrement
    </button>
  </div>

  <div class="form-wrapper">
    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="form">
            <h2 class="title">{{ isLogin ? 'Bienvenue' : 'Créer un compte' }}</h2>
            <div class="input-row" >
              <div class="input-group" :class="{ hidden: isLogin }">
                <label for="name">Nom</label>
                <input
                  id="name"
                  v-model="name"
                  type="text"
                  placeholder="Dupont"
                  :required="!isLogin"
                />
              </div>
              <div class="input-group" :class="{ hidden: isLogin }">
                <label for="firstName">Prénom</label>
                <input
                  id="firstName"
                  v-model="firstName"
                  type="text"
                  placeholder="Jean"
                  :required="!isLogin"
                />
              </div>
            </div>

            <div class="input-group">
              <label for="email">Email professionnel</label>
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="votre@entreprise.com"
                required
              />
            </div>

            <div class="input-group">
              <label for="password">Mot de passe</label>
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="********"
                required
              />
              <p style="color: red; font-size: 15px" v-if="submitted && authStore.error">{{ authStore.error }}</p>

              <!-- Indicateur de force du mot de passe (seulement en mode enregistrement) -->
              <div v-if="!isLogin" class="password-strength">
                <div class="strength-bars">
                  <div class="strength-bar" :class="{ weak: passwordStrength === 1, medium: passwordStrength === 2, strong: passwordStrength === 3 }"></div>
                  <div class="strength-bar" :class="{ medium: passwordStrength === 2, strong: passwordStrength === 3 }"></div>
                  <div class="strength-bar" :class="{ strong: passwordStrength === 3 }"></div>
                </div>
                <p class="password-requirements" v-if="!isPasswordValid">
                  Minimum requis : 16 caractères, 1 minuscule, 1 majuscule, 1 chiffre, 1 caractère spécial
                </p>
              </div>
            </div>

            <div class="input-group" :class="{ hidden: isLogin }">
              <label for="confirm-password">Confirmer le mot de passe</label>
              <input
                id="confirm-password"
                v-model="confirmPassword"
                type="password"
                placeholder="********"
                :required="!isLogin"
              />
              <p style="color: red; font-size: 15px;" v-if="submitted && password !== confirmPassword">Les mots de passe ne correspondent pas.</p>
            </div>

            <button type="submit" class="submit-btn">
              {{ isLogin ? 'Se connecter' : "Créer mon compte" }}
            </button>
          </form>
        </div>
</template>

<style scoped>
.input-row {
  display: flex;
  gap: var(--space-lg);
}

.tabs {
  width: 100%;
  align-items: center;
  display: flex;
  border-bottom: var(--border-width) solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.form-wrapper {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 60px 40px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab {
  flex: 1;
  width: 10px;
  padding: var(--space-md) 0;
  background: none;
  border: none;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
}

.tab.active {
  color: var(--text-primary);
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: calc(var(--border-width) * -1);
  left: 0;
  right: 0;
  height: var(--border-width);
  background-color: var(--primary-color);
}

.tab:hover:not(.active) {
  color: var(--text-secondary);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.title {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  max-height: 150px;
  opacity: 1;
  overflow: hidden;
  transition: max-height 0.4s ease, opacity 0.4s ease, margin 0.4s ease;
}

.input-group.hidden {
  max-height: 0;
  opacity: 0;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

.input-group label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
}

.input-group input {
  padding: var(--space-md) var(--space-lg);
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-md);
  transition: all var(--transition-base);
  background-color: var(--bg-input);
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--secondary-color);
}

.input-group input::placeholder {
  color: var(--text-placeholder);
}

.submit-btn {
  padding: 14px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-top: var(--space-sm);
}

.submit-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.submit-btn:active {
  transform: translateY(0);
}

/* Password strength indicator */
.password-strength {
  margin-top: var(--space-sm);
}

.strength-bars {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.strength-bar {
  flex: 1;
  height: 4px;
  background-color: var(--border-color);
  border-radius: 2px;
  transition: background-color var(--transition-base);
}

.strength-bar.weak {
  background-color: #ff4444;
}

.strength-bar.medium {
  background-color: var(--color-warning);
}

.strength-bar.strong {
  background-color: var(--color-success);
}

.password-requirements {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: var(--space-xs);
}
</style>
