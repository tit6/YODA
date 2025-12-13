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
  gap: 16px;
}

.tabs {
  width: 100%;
  align-items: center;
  display: flex;
  border-bottom: 2px solid #e5e5e5;
  position: sticky;
  top: 0;
  z-index: 10;
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
  padding: 12px 0;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-active-color);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab.active {
  color: var(--primary-color);
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--primary-color);
}

.tab:hover:not(.active) {
  color: var(--primary-hover-color);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.input-group input::placeholder {
  color: #999;
}

.submit-btn {
  padding: 14px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

.submit-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.submit-btn:active {
  transform: translateY(0);
}

/* Password strength indicator */
.password-strength {
  margin-top: 8px;
}

.strength-bars {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background-color: #e5e5e5;
  border-radius: 2px;
  transition: background-color 0.3s ease;
}

.strength-bar.weak {
  background-color: #ff4444;
}

.strength-bar.medium {
  background-color: #ffaa00;
}

.strength-bar.strong {
  background-color: #00c851;
}

.password-requirements {
  font-size: 12px;
  color: var(--primary-active-color);
  margin-top: 4px;
}
</style>
