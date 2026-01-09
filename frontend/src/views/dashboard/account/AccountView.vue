<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { PrivateKeyExport } from '@/stores/crypto'
import PasswordA2FModal from './components/PasswordA2FModal.vue'
import ActivateA2FModal from './components/ActivateA2FModal.vue'
import DisableA2FModal from './components/DisableA2FModal.vue'
import ExportPrivateKeyModal from './components/ExportPrivateKeyModal.vue'

const authStore = useAuthStore()
const showPasswordModal = ref(false)
const showA2FModal = ref(false)
const showDisableA2FModal = ref(false)
const showExportModal = ref(false)
const qrCodeBase64 = ref('')
const secretKey = ref('')
const isA2FActive = ref(false)
const exportError = ref('')
const isExporting = ref(false)

const oldPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const passwordChangeSubmitted = ref(false)
const passwordChangeError = ref('')

const passwordStrength = computed(() => {
  if (!newPassword.value) return 0

  let strength = 0
  const pwd = newPassword.value

  if (pwd.length >= 16) strength++
  if (/[a-z]/.test(pwd)) strength++
  if (/[A-Z]/.test(pwd)) strength++
  if (/[0-9]/.test(pwd)) strength++
  if (/[^a-zA-Z0-9]/.test(pwd)) strength++

  if (strength <= 2) return 1
  if (strength <= 4) return 2
  return 3
})

const isPasswordValid = computed(() => {
  const pwd = newPassword.value
  return pwd.length >= 16 &&
         /[a-z]/.test(pwd) &&
         /[A-Z]/.test(pwd) &&
         /[0-9]/.test(pwd) &&
         /[^a-zA-Z0-9]/.test(pwd)
})

async function check_password_a2f() {
  if (isA2FActive.value) {
    showDisableA2FModal.value = true
  } else {
    showPasswordModal.value = true
  }
}

function closePasswordModal() {
  showPasswordModal.value = false
}

function handlePasswordSuccess(qrcode: string, secret: string) {
  showPasswordModal.value = false
  showA2FModal.value = true
  qrCodeBase64.value = qrcode
  secretKey.value = secret
}

function closeA2FModal() {
  showA2FModal.value = false
}

async function handleA2FSuccess() {
  await status_a2f()
  showA2FModal.value = false
}

async function status_a2f() {
  const response = await fetch('/api/statue_a2f', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      credentials: 'include'
    })

  let data = await response.json()
  let statusss = document.getElementById("status_a2f")
  let btn = document.getElementById("a2f_button");

  if (data.status === 2) {
    isA2FActive.value = true
    if (statusss && btn) {
      statusss.classList.remove("inactive")
      statusss.classList.add("active")
      statusss.textContent = "Activée"
      btn.textContent = "Désactiver";
      btn.style.backgroundColor = "#EF1C43";
    }
  } else {
    isA2FActive.value = false
    if (statusss && btn) {
      statusss.classList.remove("active")
      statusss.classList.add("inactive")
      statusss.textContent = "Désactivée"
      btn.textContent = "Activer";
      btn.style.backgroundColor = "";
    }
  }

}

function closeDisableA2FModal() {
  showDisableA2FModal.value = false
}

async function handleDisableA2FSuccess() {
  await status_a2f()
  showDisableA2FModal.value = false
}

async function handleChangePassword() {
  passwordChangeSubmitted.value = true
  passwordChangeError.value = ''

  if (newPassword.value !== confirmNewPassword.value) {
    passwordChangeError.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  if (!isPasswordValid.value) {
    passwordChangeError.value = 'Le mot de passe ne respecte pas les critères requis.'
    return
  }

  try {
    const response = await fetch('/api/change_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        old_password: oldPassword.value,
        new_password: newPassword.value,
        confirme_password: confirmNewPassword.value
      }),
      credentials: 'include'
    })

    const data = await response.json()

    if (response.ok && data.status === 'success') {
      alert('Mot de passe changé avec succès')
      oldPassword.value = ''
      newPassword.value = ''
      confirmNewPassword.value = ''
      passwordChangeSubmitted.value = false
    } else {
      passwordChangeError.value = 'Ancien mot de passe incorrect'
    }
  } catch (error) {
    console.error('Erreur:', error)
    passwordChangeError.value = 'Erreur de connexion'
  }
}

function openExportModal() {
  showExportModal.value = true
  exportError.value = ''
}

function closeExportModal() {
  showExportModal.value = false
  exportError.value = ''
}

async function handleExportPrivateKey(passphrase: string, confirmPassphrase: string) {
  exportError.value = ''

  // Validation des champs
  if (!passphrase) {
    exportError.value = 'Veuillez saisir une passphrase'
    return
  }

  if (passphrase.length < 12) {
    exportError.value = 'La passphrase doit contenir au moins 12 caractères'
    return
  }

  if (passphrase !== confirmPassphrase) {
    exportError.value = 'Les passphrases ne correspondent pas'
    return
  }

  isExporting.value = true

  try {
    // Export et chiffrement de la clé privée
    const exportedData = await PrivateKeyExport.exportPrivateKey(passphrase)

    // Téléchargement du fichier
    PrivateKeyExport.downloadExportFile(exportedData)

    alert('Clé privée exportée avec succès!\n\nIMPORTANT: Conservez votre passphrase en lieu sûr.\nSans elle, vous ne pourrez pas restaurer votre clé privée.')

    closeExportModal()
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
    exportError.value = 'Erreur lors de l\'export de la clé privée. Assurez-vous qu\'une clé existe.'
  } finally {
    isExporting.value = false
  }
}

onMounted(() => {
  status_a2f();
})
</script>

<template>
  <div class="main-content">
    <h2 class="page-title">Paramètres du compte</h2>

    <div class="section">
      <h3 class="section-title">Mot de passe</h3>
      <form @submit.prevent="handleChangePassword" class="change-password-form">
        <div class="input-group">
          <label for="old-password">Ancien mot de passe</label>
          <input
            id="old-password"
            v-model="oldPassword"
            type="password"
            placeholder="Entrez votre mot de passe actuel"
            required
          />
        </div>
        <div class="input-group">
          <label for="new-password">Nouveau mot de passe</label>
          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            placeholder="Entrez votre nouveau mot de passe"
            required
          />

          <div class="password-strength">
            <div class="strength-bars">
              <div class="strength-bar" :class="{ weak: passwordStrength === 1, medium: passwordStrength === 2, strong: passwordStrength === 3 }"></div>
              <div class="strength-bar" :class="{ medium: passwordStrength === 2, strong: passwordStrength === 3 }"></div>
              <div class="strength-bar" :class="{ strong: passwordStrength === 3 }"></div>
            </div>
            <p class="password-requirements" v-if="newPassword && !isPasswordValid">
              Minimum requis : 16 caractères, 1 minuscule, 1 majuscule, 1 chiffre, 1 caractère spécial
            </p>
          </div>
        </div>
        <div class="input-group">
          <label for="confirm-password">Confirmer le nouveau mot de passe</label>
          <input
            id="confirm-password"
            v-model="confirmNewPassword"
            type="password"
            placeholder="Confirmez votre nouveau mot de passe"
            required
          />
        </div>

        <p v-if="passwordChangeSubmitted && passwordChangeError" class="error-message">{{ passwordChangeError }}</p>

        <button type="submit" class="submit-btn">Changer le mot de passe</button>
      </form>
    </div>

    <div class="section">
      <h3 class="section-title">Authentification à double facteur</h3>
      <div class="a2f-container">
        <div class="a2f-info">
          <p class="a2f-status">
            Statut : <span class="status-badge" id="status_a2f"></span>
          </p>
        </div>
        <button class="action-btn" id="a2f_button" @click="check_password_a2f"> </button>
      </div>
    </div>

    <div class="section">
      <h3 class="section-title">Clé privée</h3>
      <div class="export-container">
        <p class="export-description">
          Sauvegardez votre clé privée pour pouvoir restaurer votre compte en cas de besoin.
        </p>
        <button class="export-btn" @click="openExportModal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Sauvegarder ma clé privée
        </button>
      </div>
    </div>
  </div>

  <!-- Modals -->
  <PasswordA2FModal
    :show="showPasswordModal"
    @close="closePasswordModal"
    @success="handlePasswordSuccess"
  />

  <ActivateA2FModal
    :show="showA2FModal"
    :qr-code-base64="qrCodeBase64"
    :secret-key="secretKey"
    @close="closeA2FModal"
    @success="handleA2FSuccess"
  />

  <DisableA2FModal
    :show="showDisableA2FModal"
    @close="closeDisableA2FModal"
    @success="handleDisableA2FSuccess"
  />

  <ExportPrivateKeyModal
    :show="showExportModal"
    :error="exportError"
    :is-exporting="isExporting"
    @close="closeExportModal"
    @export="handleExportPrivateKey"
  />

</template>

<style scoped>
.main-content {
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  padding: var(--space-xxl);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  gap: var(--space-xxl);
}

.page-title {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0;
}

.section {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding-bottom: var(--space-xxl);
  border-bottom: var(--border-width) solid var(--border-color);
}

.section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

/* Password Section */
.change-password-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.submit-btn {
  padding: 14px var(--space-xl);
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  align-self: flex-start;
  margin-top: var(--space-xs);
}

.submit-btn:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 2FA Section */
.a2f-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xl);
  background-color: var(--bg-input);
  border: var(--border-width) solid var(--border-input-color);
  border-radius: var(--border-radius-md);
  gap: var(--space-xl);
}

.a2f-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  flex: 1;
}

.a2f-status {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.status-badge {
  display: inline-block;
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.status-badge.inactive {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
}

.status-badge.active {
  background-color: var(--color-success-bg);
  color: var(--color-success-dark);
}

.action-btn {
  padding: var(--space-md) var(--space-xl);
  background-color: var(--primary-color);
  color: var(--secondary-color);
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.action-btn:active {
  transform: translateY(0);
}

/* Export Section */
.export-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.export-description {
  font-size: var(--font-size-md);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 14px var(--space-xl);
  border: none;
  background: var(--primary-color);
  cursor: pointer;
  color: var(--secondary-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  transition: all var(--transition-base);
  align-self: flex-start;
}

.export-btn:hover {
  background: var(--primary-hover-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.export-btn:active {
  transform: translateY(0);
}

.export-btn svg {
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    padding: var(--space-xl);
    gap: var(--space-xl);
  }

  .page-title {
    font-size: var(--font-size-3xl);
  }

  .section-title {
    font-size: var(--font-size-xl);
  }

  .a2f-container {
    flex-direction: column;
    align-items: stretch;
  }

  .action-btn {
    width: 100%;
  }

  .submit-btn,
  .export-btn {
    width: 100%;
    justify-content: center;
  }
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
  margin: var(--space-xs) 0 0 0;
}

</style>