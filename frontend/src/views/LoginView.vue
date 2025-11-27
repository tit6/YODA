<script setup lang="ts">
import { ref } from 'vue'

const isLogin = ref(true)
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const name = ref('')
const submitted = ref(false)

const handleSubmit = () => {
  submitted.value = true

  if (isLogin.value) {



    console.log('Login:', { email: email.value, password: password.value })
  } else {
    if (password.value !== confirmPassword.value) {
      const confirmPasswordError = document.getElementById('confirm-password')
      if (confirmPasswordError) {
        confirmPasswordError.style.borderColor = '#FF5465'
      }
    }

    console.log('Register:', { name: name.value, email: email.value, password: password.value })
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-content">
      <!-- Left part -->
      <div class="form-section">
        <div class="form-wrapper">
          <!-- Switch tabs -->
          <div class="tabs">
            <button
              :class="['tab', { active: isLogin }]"
              @click="isLogin = true"
            >
              Connexion
            </button>
            <button
              :class="['tab', { active: !isLogin }]"
              @click="isLogin = false"
            >
              Enregistrement
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit; submitted = true" class="form">
            <h2 class="title">{{ isLogin ? 'Bienvenue' : 'Créer un compte' }}</h2>

            <div class="input-group" :class="{ hidden: isLogin }">
              <label for="name">Nom</label>
              <input
                id="name"
                v-model="name"
                type="text"
                placeholder="Votre nom"
                :required="!isLogin"
              />
            </div>

            <div class="input-group">
              <label for="email">Email</label>
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="votre@email.com"
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
              <p style="color: red; font-size: 15px" v-if="submitted && password !== 'louis'">Le mots de passe ou nom d'utilisateur est invalide.</p>
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
              {{ isLogin ? 'Se connecter' : "S'enregistrer" }}
            </button>
          </form>
        </div>
      </div>

      <!-- Right part -->
      <div class="right-section">
        <div class="overlay">
          <h1 class="brand-title">YODA</h1>
          <p class="brand-subtitle">Votre coffre fort numérique.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-color);
  padding: 20px;
}

.login-content {
  display: flex;
  width: 100%;
  max-width: 1200px;
  height: 650px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Left */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background-color: #ffffff;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 40px;
  border-bottom: 2px solid #e5e5e5;
}

.tab {
  flex: 1;
  padding: 12px 0;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 600;
  color: #666;
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
  max-height: 100px;
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
  border: 2px solid #e5e5e5;
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

/* Right side - Image */
.right-section {
  flex: 1;
  background: linear-gradient(135deg, #1a1a1a 0%, var(--primary-color) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.overlay {
  position: relative;
  z-index: 1;
  text-align: center;
  color: var(--secondary-color);
  padding: 40px;
}


/* Branding */
.brand-title {
  font-size: 64px;
  font-weight: 900;
  letter-spacing: 8px;
  margin-bottom: 16px;
  text-shadow: 2px 2px 20px rgba(255, 255, 255, 0.3);
}

.brand-subtitle {
  font-size: 18px;
  font-weight: 300;
  letter-spacing: 2px;
  opacity: 0.9;
}

</style>
